import glob
a=1
read_files = glob.glob("*.txt")

with open("result.dat", "wb") as output:
    output.write('<collection>\n')	
    for f in read_files:
        output.write('<page>\n<id>')
        output.write(str(a))     
        a=a+1
        output.write('</id>\n<title>'+f+r'</title>')
        output.write('\n<text>')              
        with  open(f, 'rb') as input:
	    	while True:
		        data = input.read(100000)
		        if data == '':  # end of file reached
		            break
		        output.write(data)
        output.write(r"</text>")
        output.write("\n</page>\n")
    output.write('</collection>')	