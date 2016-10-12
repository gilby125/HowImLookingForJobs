# HowImLookingForJobs
A script which automatically looks for jobs on the famous job search engine "indeed" and notify users of new entries.

## Dependencies :
  * Python3.5 with :
      * requests
      * beautifulsoup4
      * websockets
      * lxml
  * phantomjs

## Usage :

  Please configure the script using config.json :

    {
      "email": "my_email@email_provider.com",       => your email address
      "email_pwd": "my_password",                   => your email account password
      "email_smtp": "smtp.mail_provider.com:587",   => the smtp address and port of your email provider
      "jobs": [
	       "developer",
	       "développeur"
      ],                                            => at least one of these words has to be in search results
      "country": "ch",                              => the country of the jobs you want the script to search for
      "city": "genève",                             => the city of the jobs you want the script to search for
      "canton": "GE",                               => the canton of the jobs you want the script to search for
      "postcode": "",                               => the postcode of the jobs you want the script to search for
      "radius": "25",                               => the search radius from the location you've specified
      "delay": 300                                  => the delay before the script checks for new jobs
    }

  The script is launched using the two following commands in separate terminals in that order :

    > python indeed.py
    > phantomjs jsinterpreter.js
