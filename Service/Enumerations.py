from enum import Enum
import numpy as np

class CarlaActor(Enum):
    Vehicle = "vehicle"
    VideoCam = "videocam"

#to distinguish between different data types
class DataType(Enum):
    UINT8 = 0
    UINT32 = 1
    FLOAT16 = 2
    FLOAT32 = 3
    INT32 = 4

#to distinguish between different image modalities
class ImageModality(Enum):
    INPUT = 0
    SEGMENTATION = 1
    DEPTH = 2

#define a methdo for the data type size in bytes
dtype_map = {
    DataType.UINT8: np.uint8,
    DataType.UINT32: np.uint32,
    DataType.FLOAT16: np.float16,
    DataType.FLOAT32: np.float32,
    DataType.INT32: np.int32,
}
