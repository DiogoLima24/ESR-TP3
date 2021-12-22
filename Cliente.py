import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI

if __name__ == "__main__":
	try:
		addr = sys.argv[1]
		fluxo = int(sys.argv[2])
		port = 25000
	except:
		print("[Usage: Cliente.py <local_ip> <fluxo>]\n")
	
	root = Tk()
	
	# Create a new client
	app = ClienteGUI(root, addr, port,fluxo)
	app.master.title("Cliente Exemplo")	
	root.mainloop()
	
