This is the start of a library to retrieve and hopefully locally archive course information from canvas.instructure.com using the API documented at https://canvas.instructure.com/doc/api/index.html

I'm open to changes, suggestions and pull requests.

To use this, you must create an API key under "Approved Integrations" on your cavas profile page.
Then copy config.conf.sample to config.conf and change the token to your API key and school to the name of your school as it appears in the canvas URL.

This uses python 3.x.

required libraries:
joblib: 	https://joblib.readthedocs.io/en/latest/

html2text:	https://pypi.org/project/html2text/

Happy Hacking!!
