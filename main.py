import cv2
import imutils
from flask_opencv_streamer.streamer import Streamer
from imageai.Detection.Custom import CustomVideoObjectDetection
from google.cloud import storage

bucket_name = "fleet-tractor-308119.appspot.com"
source_blob_name = "detection_model-ex-017--loss-0022.945.h5"
destination_file_name = "new_model.h5"

storage_client = storage.Client(project="fleet-tractor-308119")

bucket = storage_client.bucket(bucket_name)

blob = bucket.blob(source_blob_name)
blob.download_to_filename(destination_file_name)

print(
    "Blob {} downloaded to {}.".format(
        source_blob_name, destination_file_name
    )
)

port = 8080
require_login = False
streamer = Streamer(port, require_login)

camera = cv2.VideoCapture("https://s2.moidom-stream.ru/s/public/0000010491.m3u8")

detector = CustomVideoObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("new_model.h5")
detector.setJsonPath("detection_config.json")
detector.loadModel()


def forFrame(frame_number, output_array, output_count, return_detected_frame):
    frame_video = imutils.resize(return_detected_frame, width=800)
    if frame_number % 100 == 0:
        if 'empty_spot' in output_count:
            print("Free parked spots: ", output_count['empty_spot'])
            cv2.putText(frame_video, "Free parked spots {}".format(output_count['empty_spot']), (200, 30),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (30, 144, 255), 1)
        else:
            print("Free parked spots: 0")
            cv2.putText(frame_video, "Free parked spots: 0", (200, 30),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (30, 144, 255), 1)
        if 'occupied_spot' in output_count:
            print("Occupied parked spots ", output_count['occupied_spot'])
            cv2.putText(frame_video, "Occupied parked spots {}".format(output_count['occupied_spot']), (200, 60),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (30, 144, 255), 1)
        else:
            print("Occupied parked spots: 0")
            cv2.putText(frame_video, "Occupied parked spots: 0", (200, 60),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (30, 144, 255), 1)

        streamer.update_frame(frame_video)
        if not streamer.is_streaming:
            streamer.start_streaming()
        # cv2.imshow(frame_video)
        print("------------END OF A FRAME --------------")


detector.detectObjectsFromVideo(camera_input=camera,
                                display_percentage_probability=True,
                                display_object_name=True,
                                frame_detection_interval=100,
                                frames_per_second=10,
                                minimum_percentage_probability=40,
                                log_progress=False,
                                per_frame_function=forFrame,
                                save_detected_video=False,
                                return_detected_frame=True)
