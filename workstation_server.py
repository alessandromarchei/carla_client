import argparse
import time
import os
import cv2
import numpy as np

from TCP.ServerSender import ServerSender
from TCP.ServerReceiver import ServerReceiver
from TCP.Buffer import BlockingQueue

from TCP.utils.visualization import add_mask_segmentation


"""
Normal mode : scan the input folder and send images at fixed rate
Manual send mode : wait for user input to send the next image with the sendDataForPrediction() function
"""
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--image-folder", type=str)
    parser.add_argument("--manual-send", action="store_true")

    parser.add_argument("--port-tx", type=int, default=8080)
    parser.add_argument("--port-rx", type=int, default=8081)
    parser.add_argument("--fps", type=float, default=10.0)

    parser.add_argument("--viz", action="store_true")
    parser.add_argument("--save", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    sender_queue = BlockingQueue()
    sent_queue = BlockingQueue()

    sender = ServerSender(
        args.port_tx,
        sender_queue,
        sent_queue,
        fps=args.fps,
        input_folder=None if args.manual_send else args.image_folder
    )

    receiver = ServerReceiver(args.port_rx, sent_queue)

    sender.start()
    receiver.start()

    # wait until both connections established
    print("[Main] Waiting for client connections...")
    while sender.client_sock is None or receiver.client_sock is None:
        time.sleep(0.05)

    print("[Main] Connected. Starting streaming loop.")

    # MANUAL SEND MODE
    if args.manual_send:
        folder = os.path.expanduser(args.image_folder)
        files = sorted(os.listdir(folder))

        frame_id = 0

        for fname in files:
            img = cv2.imread(os.path.join(folder, fname))
            if img is None:
                continue

            frame_id += 1
            sender.sendDataForPrediction(img, frame_id)
            time.sleep(1.0 / args.fps)

    # MAIN VIS LOOP for each image in folder img.len()
    for _ in range(len(files)):
        result = receiver.receiveDataFromPrediction()
        if result is None:
            time.sleep(0.01)
            continue

        frame, mask = result
        img = frame["img"]
        f_id = frame["frame_id"]

        if args.viz:
            overlay = add_mask_segmentation(img, mask, alpha=0.5)
            cv2.imshow("SceneSeg", overlay)
            cv2.waitKey(1)

        if args.save:
            overlay = add_mask_segmentation(img, mask, alpha=1.0)
            out = np.vstack([img, overlay])
            cv2.imwrite(f"result_{f_id}.png", out)


if __name__ == "__main__":
    main()
