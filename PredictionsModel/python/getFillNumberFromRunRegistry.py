import sys
import runregistry


# Get arguments : run_num

run_num = 0
stream = ''

narg = len(sys.argv)
if narg < 2:
    print('Syntax: python3 getFillFromRun.py run_number')
    exit()
else:
    if not sys.argv[1].isdigit():
        print('First argument should be a number')
        exit()
    else : 
        run_num = int(sys.argv[1])

# Get runs info in querying RunRegistry and filtering

run = runregistry.get_run( run_number = run_num )
#print( run)

fill_num = run['oms_attributes']['fill_number']

print('RUN    FILL')
print(run_num, fill_num)



