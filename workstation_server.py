import argparse
import time

from TCP.ServerSender import ServerSender
from TCP.ServerReceiver import ServerReceiver
from TCP.Buffer import BlockingQueue


DEFAULT_TX_PORT = 8080
DEFAULT_RX_PORT = 8081

DEFAULT_TX_RATE = 10.0    #send images at 10 Hz



def parse_args():
    parser = argparse.ArgumentParser(description="Workstation TCP Server (Python)")

    parser.add_argument(
        "-i", "--image-folder",
        required=True,
        type=str,
        help="Folder containing input images"
    )

    parser.add_argument(
        "--port-tx",
        type=int,
        default=DEFAULT_TX_PORT,
        help="TX port (server → client)"
    )
    parser.add_argument(
        "--port-rx",
        type=int,
        default=DEFAULT_RX_PORT,
        help="RX port (client → server)"
    )

    parser.add_argument(
        "--fps",
        type=float,
        default=DEFAULT_TX_RATE,
        help="Transmission frame rate (Hz)"
    )

    parser.add_argument(
        "--viz",
        action="store_true",
        help="Visualize received masks"
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save combined output images"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    tx_port = args.port_tx
    rx_port = args.port_rx
    fps = args.fps
    visualize = args.viz
    save = args.save
    image_folder = args.image_folder

    print(f"==========================")
    print(f"Starting Python Server")
    print(f"TX port: {tx_port}")
    print(f"RX port: {rx_port}")
    print(f"FPS: {fps}")
    print(f"Viz: {visualize}")
    print(f"Save: {save}")
    print(f"==========================")

    # Shared thread-safe buffer
    queue = BlockingQueue()

    # Create Sender + Receiver
    sender = ServerSender(tx_port, image_folder, queue, fps)
    receiver = ServerReceiver(rx_port, queue, visualize, save, fps)

    # Start both threads
    sender.start()
    receiver.start()

    print("[Main] Sender and Receiver threads started.")

    while sender.running:
        time.sleep(0.1)

    print("[Main] Sender thread ended, stopping...")

    sender.stop()
    receiver.stop()

    print("[Main] Server finished cleanly.")


if __name__ == "__main__":
    main()
