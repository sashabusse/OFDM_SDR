find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_OFDM_OOT gnuradio-OFDM_OOT)

FIND_PATH(
    GR_OFDM_OOT_INCLUDE_DIRS
    NAMES gnuradio/OFDM_OOT/api.h
    HINTS $ENV{OFDM_OOT_DIR}/include
        ${PC_OFDM_OOT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_OFDM_OOT_LIBRARIES
    NAMES gnuradio-OFDM_OOT
    HINTS $ENV{OFDM_OOT_DIR}/lib
        ${PC_OFDM_OOT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-OFDM_OOTTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_OFDM_OOT DEFAULT_MSG GR_OFDM_OOT_LIBRARIES GR_OFDM_OOT_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_OFDM_OOT_LIBRARIES GR_OFDM_OOT_INCLUDE_DIRS)
