"""pyexetelsms
	Exetel SMS Gateway
	Allow connections to the exetel api from python
	This was written based on api documenation: 
	http://exetel.com.au/Exetel_SMS_API_documentation.pdf

	Written By: Daniel Lawrence <daniel@danielscottlawrence.com>

"""
__version__ = "0.02"

#------------------------------------------------------------------------------
from httplib2 import Http
from urllib import urlencode
from datetime import datetime
#------------------------------------------------------------------------------
class ExetelException(Exception):
	""" Generic Exception
	All errors encounted will generate this exception.
	Each instance will have its own id, based on the message
	The messages could change as i dont control these.
	"""
	def __init__(self,id=0, message=None):
		self.id = id		# unique exception ID
		self.message = message	# unique message content from exetel

	def __str__(self):
		return "%s" % self.message
#------------------------------------------------------------------------------
# class invalidusernamepsasword(ExetelException): pass
#------------------------------------------------------------------------------

class SMS(object):
	""" SMS Object
	This object is responible for connecting to the exetel gateway and submitting a single sms
	The SMS object requires a gateway object, as a connection.
	"""
	def __init__(self, gateway, sender, mobilenumber,message,referencenumber=1):
		self.gateway = gateway
		self.sender = sender
		self.mobilenumber = mobilenumber
		self.message = message
		self.referencenumber = referencenumber
		#------------------------------------------#
		#     The Below should be Read-only.	   #
		#------------------------------------------#
		self.messagetype = "Text"
		self.exetel_id = None
		self.exetel_reference = None
		self.exetel_notes = None
		self.exetel_message = None
		self.exetel_status = None
		self.date_sent = None

	def send(self):
		""" send
		This connects to the remote exetel server and submits the SMS via https
		"""
		data={'message': self.message, 'sender': self.sender, 'mobilenumber': self.mobilenumber,
		'messagetype': self.messagetype, 'referencenumber': self.referencenumber }
		encoded_sms = urlencode(data).replace('+', '%20')
		http_uri="%s&%s" % ( self.gateway.uri_send, encoded_sms )
		print http_uri

		h = Http()
		resp, content = h.request(http_uri, "GET")
		self.exetel_notes = content
		(self.exetel_status, self.mobilenumber, self.exetel_reference, self.exetel_id, self.exetel_message) = self.exetel_notes.split('|')
		if int(self.exetel_status) == 1:
			self.date_sent = datetime.now()
			return 
		raise ExetelException(1, self.exetel_message)

	def __str__(self):
		if self.date_sent:
			return "sent '%s' to '%s' from '%s'" % ( self.message, self.mobilenumber, self.sender )
		return "sending '%s' to '%s' from '%s'" % ( self.message, self.mobilenumber, self.sender )
		

#-------------------------------------------------------------------------------------------
class Exetel(object):
	"""Exetel SMS Gateway
	This is an SMS gateway object, that allow you to
	* Check SMS Credit
	* validate your username/password
	* Send SMS
	"""
	#-------------------------------------------------------------------------------------------
	def __init__(self,username=None,password=None):
		""" The basic data used to make remote calls to exetel """
		self.username = username
		self.password = password
		self.uri_credit = "https://smsgw.exetel.com.au/sendsms/api_sms_credit.php?username=%s&password=%s" % ( self.username, self.password )
		self.uri_send = "https://smsgw.exetel.com.au/sendsms/api_sms.php?username=%s&password=%s" % ( self.username, self.password )
		self.credit = None

	#-------------------------------------------------------------------------------------------
	def get_credit(self):
		""" Update self.credit directory from the server """
		h = Http()
		resp, content = h.request(self.uri_credit, "GET")
		(remote_rc,credit,status) = content.split('|')
		if int(remote_rc) != 1:
			raise ExetelException(1, "Unable to get credit update. %s" % status)
		self.credit = float(credit)
		return self.credit

	#-------------------------------------------------------------------------------------------
	def send_sms(self, sender, mobilenumber,message,referencenumber=1):
		""" Sending a single sms to a number """
		s = SMS(self, sender, mobilenumber,message,referencenumber)
		s.send()

#-------------------------------------------------------------------------------------------
if __name__ == "__main__":
	USER = None
	PASSWORD = None

	sms_gateway = Exetel(USER, PASSWORD)
	sms_gateway.get_credit()
	print "%s has $%d in credit" % ( sms_gateway.username, sms_gateway.credit )
	
	SENDER = "PythonAPI"
	MOBILE = "0000000000"
	MESSAGE = "Test sms from python API"

	sms = SMS(sms_gateway,SENDER,MOBILE,MESSAGE)
	sms.send()
