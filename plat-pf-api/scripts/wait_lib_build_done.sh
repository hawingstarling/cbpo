#!/bin/bash
check_version=`wget -S --spider "http://python-registry.channelprecision.com/packages/django-plat-import-lib-api-${IMPORT_LIB_VERSION:1}.tar.gz"  2>&1 | grep 'HTTP/1.1 200 OK' | wc -l`

counter=0
wait=200

while (((check_version == 0)&&($counter < $wait)))
do
	echo "Checking version for the available library. Please wait for a few minute..."
	sleep 10
	((counter+=10))
	check_version=`wget -S --spider "http://python-registry.channelprecision.com/packages/django-plat-import-lib-api-${IMPORT_LIB_VERSION:1}.tar.gz"  2>&1 | grep 'HTTP/1.1 200 OK' | wc -l`
done

if [[ $counter -eq $wait ]]
then
echo "Please check the library has built successfully yet? If not, please try again."
exit 1;
fi
echo "Done!"