import cv2
import time
from ultralytics import YOLO
from brain import think

# runs the yolo model
model = YOLO("yolo11n.pt")

def detect_objects(frame):

    # create an empty list for detected objects
    detected_objects = []
    results = model(frame, verbose=False)

    # loop through YOLO results
    # get each object's class ID and name
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]

            # add the name to the list
            if object_name not in detected_objects:
                detected_objects.append(object_name)
        
    # return the list
    return detected_objects


def run_vision():

    camera = cv2.VideoCapture(0)

    last_detection = 0

    # remember how many times each object was seen
    object_memory = {}

    # remember how many times each object was missing
    missing_memory = {}

    # remember the last stable objects sent to the AI
    last_detected_objects = []

    # remember the stable objects from the previous check
    previous_stable_objects = []

    # remember recent vision events
    recent_events = []

    while True:

        success, frame = camera.read()

        if not success:
            print("Could not access camera")
            break

        current_time = time.time()

        # run object detection every 1 second
        if current_time - last_detection >= 1:
            detected_objects = detect_objects(frame)

            # update how many times each object has been seen
            for object_name in detected_objects:
                if object_name in object_memory:
                    object_memory[object_name] = object_memory[object_name] + 1
                else:
                    object_memory[object_name] = 1

            stable_objects = []

            # update how many times each object has been missing
            for object_name in object_memory:
                if object_name in detected_objects:
                    missing_memory[object_name] = 0
                else:
                    if object_name in missing_memory:
                        missing_memory[object_name] = missing_memory[object_name] + 1
                    else:
                        missing_memory[object_name] = 1

            # remove objects that have been missing for 3 checks
            for object_name in list(object_memory):
                if missing_memory[object_name] >= 3:
                    del object_memory[object_name]
                    del missing_memory[object_name]

            # add objects that have been seen 3 times to the stable list
            for object_name in object_memory:
                if object_memory[object_name] >= 3:
                    stable_objects.append(object_name)

            # label objects that are newly detected and removed
            new_objects = []
            removed_objects = []

            for object_name in stable_objects:
                if object_name not in previous_stable_objects:
                    new_objects.append(object_name)

            for object_name in previous_stable_objects:
                if object_name not in stable_objects:
                    removed_objects.append(object_name)

            # only send the objects to the AI if they changed
            if stable_objects != last_detected_objects:

                message = ""

                # tell the AI about new objects
                for object_name in new_objects:
                    message = message + "A new object appeared: " + object_name + ". "

                # tell the AI about removed objects
                for object_name in removed_objects:
                    message = message + "An object disappeared: " + object_name + ". "

                # tell the AI what is currently visible
                message = message + "Currently visible: " + ", ".join(stable_objects) + "."

                

                print("Sending to AI:", message)
                response = think(message, recent_events)

                # remember this event
                recent_events.append(message)

                # only keep the 5 most recent events
                if len(recent_events) > 5:
                    recent_events.pop(0)



                # remember the objects sent to the AI
                last_detected_objects = stable_objects

            # remember the stable objects from this check
            previous_stable_objects = stable_objects

            last_detection = current_time

        # show the camera
        cv2.imshow("Companion Robot Vision", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


run_vision()