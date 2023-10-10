from __future__ import annotations

import logging
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass


class GlobalVariable:

    NO_LOG = True
    LOG_FILE = ''
    CMD_FILE = ''

    BASE_LOGGER = logging.getLogger()
    LOG_CMD_LOGGER = logging.getLogger()
    CMD_LOGGER = logging.getLogger()

    PROCESS_CNT = 16
    LSF_CMD = 'bsub -q aaa.q -n1 -P aaa -R "rusage[mem=20GB】"'

    SOFTWARE = 'photon'

    BANNER = rf'''
|-------------------------------------------------------------------------------|
|     //-----\    //     //   //-----\    ----------   //-----\     /\       // | 
|    //     //   //     //   //      //      //       //      //   // \     //  |
|   //-----//   //-----//   //      //      //       //      //   //   \   //   |
|  //          //     //   //      //      //       //      //   //     \ //    |
| //          //     //     \-----//      //         \-----//   //       \/     |
|-------------------------------------------------------------------------------|
                         CHIP VISUALIZE TOOL - {SOFTWARE}
                            Developed By Hongji.Liu
'''

