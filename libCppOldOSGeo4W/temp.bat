setlocal
cd "E:/dev/src/python/qgis3/point_cloud_3d/libCpp"
C:/LAStools2021/bin/las2dem64 -i C:/uclm/Ejemplo_Zamora_1/PNOA_LiDAR/prueba/lat.laz -keep_class  2 -nodata  -9999 -step  1.0 -o C:/uclm/Ejemplo_Zamora_1/PNOA_LiDAR/prueba/dtm_lat.tif
endlocal
