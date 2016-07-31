#this script is used to test the different methods of autoplaying tetris
import multiprocessing as mult
from time import sleep
import sys
import matplotlib.pyplot as plt
import os
import argparse

import tetris


def graph(all_lifetimes):
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

def tetris_player_process(a, i, **kwargs):
	"""worker function that will play tetris in the background"""
	print kwargs
	App = tetris.TetrisApp(**kwargs)
	a[i] = App.run()#runs the game until it loses and returns the number of pieces 
	App.quit()

def check_records(args, records):
	if records > 0:
		args['record'] = ""
		records-=1
	else:
		args['record'] = False

def a_job_is_alive(job_list):
	return True in [job.is_alive() for job in job_list]

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Plays tetris')

	parser.add_argument('-gaz', action="store_true", default=True, dest="start_auto", help='Add -gaz for Gaz to take over and start playing automcatically')
	parser.add_argument(action="store_false", default=False, dest="screen")
	parser.add_argument('-r', action="store", default=0, type=int, dest="records_num", help='Add -r and the number of records to record all gameplays.')
	parser.add_argument('-knn', default=False, const="defaultmodel", dest="knn_modelname", nargs="?", help='Add this flag and a modelname to use KNN. If no model is provided "defaultmodel" will be used ')
	parser.add_argument('-greedy', action="store_true", default=True, dest="greedy", help='Add this flag to use a greedy algorithm. Default is True')
	parser.add_argument("-players", action="store", dest="batch_size", type=int, default=1, help="The number of games (python interpreters) running together")
	parser.add_argument("-games", action="store", dest="jobs", type=int, default=1, help="number of total games being played")

	args = parser.parse_args()
	dict_args = dict(args._get_kwargs())

	all_lifetimes = []
	jobs_list = []
	jobs = args.jobs
	lifetimes = mult.Array('i', [0]*jobs)

	#create initial batch
	for index in range(args.batch_size):
		check_records(dict_args, jobs)
 		job = mult.Process(target=tetris_player_process, args=(lifetimes, jobs-1), kwargs=dict_args)
		job.start()
		jobs_list.append(job)
		jobs -= 1	

	while jobs > 0 or a_job_is_alive(jobs_list):
		job_status = [job.is_alive() for job in jobs_list]
		a_job_is_dead = False in job_status
		if a_job_is_dead and jobs > 0:
			print "Job finished, %d jobs left" % (jobs)

			check_records(dict_args, jobs)
			finished_job_index = job_status.index(False)

			jobs_list[finished_job_index].join()
			jobs_list[finished_job_index] = mult.Process(target=tetris_player_process, args=(lifetimes, jobs-1), kwargs=dict_args)
			jobs_list[finished_job_index].start()

			jobs -= 1
		sleep(0.5)
	graph(lifetimes)
