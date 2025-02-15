import sys, socket

from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class Servidor:	

	clientInfo = {}

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05)
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break
				
			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtpAddr']
					port = int(self.clientInfo['rtpPort'])
					packet =  self.makeRtp(data, frameNumber)
					fluxo = bytes([self.clientInfo['stream']])
					packet = bytes([1]) + fluxo + packet
					self.clientInfo['rtpSocket'].sendto(packet,(address,port))
				except:
					print("Connection Error")
					print('-'*60)
					traceback.print_exc(file=sys.stdout)
					print('-'*60)
			else:
				self.clientInfo['videoStream'].reset()
		# Close the RTP socket
		self.clientInfo['rtpSocket'].close()
		print("All done!")

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		print("Encoding RTP Packet: " + str(seqnum))
		
		return rtpPacket.getPacket()

	
	def main(self):
		try:
			# Get the media file name
			addr = sys.argv[1]
			fluxo = int(sys.argv[2])
			filename = sys.argv[3]
			print("Using provided video file ->  " + filename)
		except:
			print("[Usage: Servidor.py <local_ip> <fluxo> <videofile>]\n")
			filename = "movie.Mjpeg"
			print("Using default video file ->  " + filename)

		# videoStram
		self.clientInfo['stream'] = fluxo
		self.clientInfo['videoStream'] = VideoStream(filename)
		# socket
		self.clientInfo['rtpPort'] = 25000
		self.clientInfo['rtpAddr'] = socket.gethostbyname(addr)
		print("Sending to Addr:" + self.clientInfo['rtpAddr'] + ":" + str(self.clientInfo['rtpPort']))
		# Create a new socket for RTP/UDP
		self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.clientInfo["rtpSocket"].sendto(bytes([0,fluxo]),(self.clientInfo['rtpAddr'],self.clientInfo['rtpPort']))
		self.clientInfo['event'] = threading.Event()
		self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
		self.clientInfo['worker'].start()

if __name__ == "__main__":
	(Servidor()).main()



