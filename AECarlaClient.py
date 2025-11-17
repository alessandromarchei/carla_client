#!/usr/bin/env python3
import argparse
from Gui.MainWindow import MainWindow
from Service.CarlaProcessor import CarlaProcessorService
from Service.Settings import Settings_Set
from Service.VehiclesProcessor import VehiclesProcessor


DEFAULT_VEHICLES_PATH = "configs/vehicles/"
DEFAULT_CARLA_SETTINGS_PATH="configs/carla/settings.json"
def parse_args():
    parser = argparse.ArgumentParser(
        description="CARLA GUI Client Launcher (simple argparse version)"
    )

    parser.add_argument(
        "--vehicles-path",
        type=str,
        default=DEFAULT_VEHICLES_PATH,
        help="Path to the vehicles directory (default: configs/vehicles/)"
    )

    parser.add_argument(
        "--settings",
        type=str,
        default=DEFAULT_CARLA_SETTINGS_PATH,
        help="Path to CARLA settings.json (default: configs/carla/settings.json)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    print("==========================================")
    print("     CARLA GUI Client Launcher")
    print("==========================================")
    print(f"Using vehicles: {args.vehicles_path}")
    print(f"Using settings: {args.settings}")

    # ========== Load Vehicles ==========
    vp = VehiclesProcessor()
    usedVehicles = vp.loadusedvehicles(args.vehicles_path)
    print(f"Loaded {len(usedVehicles)} vehicles")

    # ========== CARLA Connector ==========
    carlaConnector = CarlaProcessorService()

    # ========== Load Settings ==========
    settings = Settings_Set(args.settings)
    settings.deserialize()

    # ========== Start GUI ==========
    MainWindow("CARLA client 0.10",
               carlaConnector,
               usedVehicles,
               settings)


if __name__ == "__main__":
    main()
