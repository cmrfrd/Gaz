#this script is used to test the different methods of autoplaying tetris
import multiprocessing as mult
import tetris
from time import sleep
import sys
import matplotlib.pyplot as plt

def tetris_player_process(a, i):
	"""worker function that will play tetris in the background"""
	App = tetris.TetrisApp(start_auto=True, screen=False)
	processed_pieces = App.run()#runs the game until it loses and returns the number of pieces 
	a[i] = processed_pieces
	App.quit()


def all_jobs_finished(job_list):
	return False in [job.is_alive() for job in job_list] 

if __name__ == "__main__":
	batch_size = 0
	jobs = 0

	if len(sys.argv) == 3:
		batch_size = int(sys.argv[1])
		jobs = int(sys.argv[2])
	elif len(sys.argv) == 2:
		batch_size = int(sys.argv[1])
		jobs = 1
	elif len(sys.argv) == 1:
		batch_size = int(raw_input("Batch size: "))
		jobs = int(raw_input("Jobs: "))
	else:
		print "Usage: [number of batches] [number of jobs]"		
	#command line arguments things	
	
	all_lifetimes = []
	jobs_list = []
	lifetimes = mult.Array('i', [0]*jobs)

	print "Creating Initial Batch"
	for index in range(batch_size):#create initial job list from batch size
		job = mult.Process(target=tetris_player_process, args=(lifetimes, jobs-1))
		print "HELLO"
		job.start()
		jobs_list.append(job)
		jobs -= 1	

	while not all_jobs_finished(jobs_list) or jobs > 0:#while all the jobs are still alive and there are still more jobs
		jobs_alive = [job.is_alive() for job in jobs_list]#get the jobs life status
		print jobs_alive
		if False in jobs_alive and jobs > 0:#if a job is finished and there are still jobs
			print "adding new job"
			finished_job_index = jobs_alive.index(False)
			jobs_list[finished_job_index].join()#find the job and join it
			jobs_list[finished_job_index] = mult.Process(target=tetris_player_process, args=(lifetimes, jobs-1))
			jobs_list[finished_job_index].start()
			jobs -= 1
			#create new job and decrease total number of jobs
		sleep(0.5)

	all_lifetimes = lifetimes

	plt.figure(figsize=(12, 9))  
  
	ax = plt.subplot(111)  
	ax.spines["top"].set_visible(False)  
	ax.spines["right"].set_visible(False)  
  
	ax.get_xaxis().tick_bottom()  
	ax.get_yaxis().tick_left()  

	plt.xticks(fontsize=14)  
	plt.yticks(range(0, 5), fontsize=14)  

	plt.xlabel("Pieces Played", fontsize=16)  
	plt.ylabel("Count", fontsize=16)  

	plt.hist(all_lifetimes,  
        	 color="#3F5D7D", bins=100)  

	plt.show()
