 Docker image to generate the SP list for hexaa backend with metadata source url in the parameters. 

You can list several space separated metadata source urls. 

Usage
-----
example:

docker run -t --rm --name hexaa-service-entityids-generator szabogyula/hexaa-service-entityids-generator https://metadata.eduid.hu/current/href.xml > hexaa_entityids.yml