setlocal
cd "C:/Users/David.Hernandez/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/point_cloud_3d/libCpp"
C:/LAStools2019/bin/las2dem64 -i X:/tical/20200507/vora-riu-03052020_dhl.laz -keep_class  2 -nodata  -9999 -step  0.2 -o X:/tical/20200507/vora-riu-03052020_dtm.tif
endlocal
