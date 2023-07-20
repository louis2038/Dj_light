import numpy as np
from seaborn import blend_palette 
from seaborn import color_palette
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile
import pygame
import math
import pygame.mixer
import time
import threading
import copy
import colorsys
import serial
from threading import Lock
import os

# folder path
dir_path = r'D:\\FICHIER\\Louis\\programmation\\DJftt\\MUSIQUE'

# list file and directories
res = os.listdir(dir_path)
for i in range(len(res)):
	print(i," - ",res[i])

## debut
while True:
	try:
		sel_mus = int(input("musique ->"))
		break
	except:
		print("erreur input")

SIZEx = 1025
SIZEy = 700
pygame.font.init()
police = pygame.font.SysFont("monospace",20)
MUS = ".\\MUSIQUE\\"+res[sel_mus]
DURE = 0
SUR = None
MAX = 5
pygame.init()
pygame.display.set_caption("Dj_lights")
screen = pygame.display.set_mode((SIZEx,SIZEy))
NBS_COLOR = 500
Color_map = color_palette("magma",NBS_COLOR)
for i in range(NBS_COLOR):
	Color_map[i] = (int(Color_map[i][0]*255),int(Color_map[i][1]*255),int(Color_map[i][2]*255))
clock = pygame.time.Clock()
PALETTE_SIZE = 20

filtre_actuel = 0
mode = [0,0,0,0,0,0,0,0]
image_text = police.render( str(filtre_actuel+1),1,(255,0,0),(0,0,0))

color_freq = [[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)]]
color_ampli = [[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)],[(0,0,0)]]
### select COM ===============================================


conn = serial.Serial(port="COM6",
	baudrate=115200,
	timeout=10)
conn2 = serial.Serial(port="COM4",
	baudrate=115200,
	timeout=10)
time.sleep(3)
# sleep to ensure ample time for computer to make serial connection 



### select COM ===============================================

"""
def choice_color(N):
	global affiche_main,color_freq
	affiche_main = False
	hue = 0
	inter = 1/360
	pygame.draw.line(screen,(250,250,250),(400,0),(400,360) )
	pygame.draw.line(screen,(250,250,250),(0,360),(400,360) )
	for i in range(360):
		col = colorsys.hsv_to_rgb(hue, 1, 1)
		pygame.draw.line(screen,(int(col[0]*255),int(col[1]*255),int(col[2]*255)),(400-30,i),(400,i) )
		hue += inter
	running = True
	sel_hu = False
	colors = []
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					nn = len(colors)
					if nn > 1:
						color_freq[filtre_actuel] = blend_palette(colors, n_colors=N, as_cmap=False, input='rgb')
					elif nn == 1:
						color_freq[filtre_actuel] = [colors[0] for _ in range(N)]
					affiche_main = True
					return
			if event.type == pygame.MOUSEBUTTONDOWN:
				x_pos,y_pos = pygame.mouse.get_pos()
				if  (370 < x_pos <= 400) and (0 <= y_pos <= 360):
					hu = y_pos/360
					sel_hu = True
					for x in range(360):
						for y in range(360):
							r,g,b = colorsys.hsv_to_rgb(hu, x/360, y/360)
							screen.set_at((x, y),(int(r*250),int(g*250),int(b*250)) )
				elif (0 <= x_pos <= 360) and (0 <= y_pos <= 360):
					if sel_hu:
						colors.append(colorsys.hsv_to_rgb(hu, x_pos/360, y_pos/360))
		
		pygame.display.flip()

	return
"""

class Dj:

	def __init__(self):
		self.S = None # data of sound
		self.size_freq = None # valeur des fréquence
		self.size_time = None # nombre de valeur d'intensité
		self.bruit = 8 # enleve le bruit du son
		self.dure_bloc = 500
		self.hauteur_barre = 2
		self.largeur_pix = 7
		self.surface = None
		self.max = 25
		

	def load_music(self,txt):
		global DURE
		y_, sr_ = librosa.load(txt,offset=0)
		DURE = int(librosa.get_duration(y=y_, sr=sr_))
		y, sr = librosa.load(txt,offset=0,duration=DURE)
		pygame.mixer.music.load(txt)
		S_ = abs(librosa.stft(y,n_fft=2048))
		self.S = librosa.power_to_db(S_,ref=1.0, amin=1e-05, top_db=80.0)
		Freq = librosa.fft_frequencies(sr=sr, n_fft=2048)
		self.size_freq,self.size_time = self.S.shape

	def create_display_bloc(self,num_bloc,lock):
		global SUR,MAX,NBS_COLOR
		lock.acquire() # je block les variables SUR,MAX et NBS_COLOR
		surface = pygame.Surface((SIZEx,self.dure_bloc*self.hauteur_barre))

		for i in range(self.dure_bloc): # tps de la music
			y_coord = i*self.hauteur_barre
			for j in range(self.size_freq): # selection de la freq
				x_coord = j*self.largeur_pix
				x_coord_bis = x_coord + self.largeur_pix
				carre = pygame.Rect(x_coord,y_coord,x_coord_bis-x_coord,self.hauteur_barre)
				val = self.S[j,i + (num_bloc*self.dure_bloc)]
				if val-self.bruit > MAX:
					MAX = val-self.bruit
				ind_color = int( (val-self.bruit)/MAX * NBS_COLOR  )
				if ind_color >= NBS_COLOR:
					ind_color = NBS_COLOR - 1
				if ind_color < 0:
					ind_color = 0
				
				pygame.draw.rect(surface,Color_map[ind_color],carre)
		SUR = surface
		lock.release()


	def main_boucle(self):
		global MAX,Color_map,filtre_actuel,image_text,arduino,PINr,PINg,PINb
		affiche_main = True
		running = True
		inter = (DURE/self.size_time)/self.hauteur_barre
		num_bloc = 0
		time_ct = 0
		cpt_bloc = 2
		total_bloc = DURE // self.dure_bloc

		start = True
		start_led = True
		bb1 = True
		pas_coord = self.dure_bloc*self.hauteur_barre
		pos1 = 0
		pos2 = pas_coord


		lock = Lock()
		Dj.create_display_bloc(self,0,lock)
		sur1 = SUR.copy()
		Dj.create_display_bloc(self,1,lock)
		sur2 = SUR.copy()
		screen.fill((0,0,0))
		screen.blit(sur1,(0,pos1))
		screen.blit(sur2,(0,pos2))
		pygame.display.flip()

		pygame.mixer.music.play(loops=0, start=0)
		t1 = time.time()
		t2 = time.time()
		tps_i = 0
		active = [0,0,0] # filtre des 3 carré du bas
		gg = [False,False,False,False,False,False,False,False]
		x_prec = None
		g_filte = [0,0,0,0,0,0,0,0]
		d_filtre = [0,0,0,0,0,0,0,0]
		cap_filtre = [1,1,1,1,1,1,1,1]
		defin = [False,False,False,False,False,False,False,False]
		freq_max = [0,0,0,0,0,0,0,0]
		ind_col = [0,0,0,0,0,0,0,0] #indice de la color map pour le mode 1


		sur_color =  pygame.Surface((SIZEx,PALETTE_SIZE))
		x_inter = SIZEx//NBS_COLOR
		for i in range(NBS_COLOR):
			rr = pygame.Rect(x_inter*i,0,x_inter,PALETTE_SIZE)
			pygame.draw.rect(sur_color,Color_map[i],rr)
		
		carre_cot = [pygame.Rect(SIZEx-50,SIZEy-20-(50*(i+1)),50,50) for i in range(8)]
		carre_bas = [pygame.Rect(SIZEx//2-50,SIZEy-70,50,50),pygame.Rect(SIZEx//2,SIZEy-70,50,50),pygame.Rect(SIZEx//2+50,SIZEy-70,50,50)]
		
		black1 = True
		black2 = True
		black3 = True

		while running:
			if affiche_main:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						#th_led.join()
						#th.join()
						running = False
					if event.type == pygame.MOUSEBUTTONDOWN:
						x_pos,y_pos = pygame.mouse.get_pos()
						if y_pos < SIZEy - PALETTE_SIZE:
							if x_prec != None:
								g_filte[filtre_actuel] = x_prec
								d_filtre[filtre_actuel] = x_pos
								N = (x_pos // self.largeur_pix)-(x_prec // self.largeur_pix)+1
								affiche_main = False
								# pre chargement de affichage palette couleur
								hue = 0
								inter_hu = 1/360
								pygame.draw.line(screen,(250,250,250),(400,0),(400,360) )
								pygame.draw.line(screen,(250,250,250),(0,360),(400,360) )
								for i in range(360):
									col = colorsys.hsv_to_rgb(hue, 1, 1)
									pygame.draw.line(screen,(int(col[0]*255),int(col[1]*255),int(col[2]*255)),(400-30,i),(400,i) )
									hue += inter_hu
								sel_hu = False
								colors = []
								x_prec = None
							else:
								x_prec = x_pos
						else:
							cap_filtre[filtre_actuel] = (MAX * (x_pos/x_inter)) / NBS_COLOR
							#print(cap_filtre)
				
					if event.type == pygame.KEYDOWN:
						print(event)
						if event.key == pygame.K_m:
							MAX = 0
							self.bruit -= 1
							print("bruit : ", self.bruit)
						if event.key == pygame.K_p:
							MAX = 0
							self.bruit += 1
							print("bruit : ", self.bruit)
						if event.key == 49:
							filtre_actuel = 0
						if event.key == 50:
							filtre_actuel = 1
						if event.key == 51:
							filtre_actuel = 2
						if event.key == 52:
							filtre_actuel = 3
						if event.key == 53:
							filtre_actuel = 4
						if event.key == 54:
							filtre_actuel = 5
						if event.key == 55:
							filtre_actuel = 6
						if event.key == 56:
							filtre_actuel = 7


						if event.key == pygame.K_q:
							active[1] = 0
						if event.key == pygame.K_s:
							active[1] = 1
						if event.key == pygame.K_d:
							active[1] = 2
						if event.key == pygame.K_f:
							active[1] = 3
						if event.key == pygame.K_g:
							active[1] = 4
						if event.key == pygame.K_h:
							active[1] = 5
						if event.key == pygame.K_j:
							active[1] = 6
						if event.key == pygame.K_k:
							active[1] = 7

						if event.key == pygame.K_a:
							active[0] = 0
						if event.key == pygame.K_z:
							active[0] = 1
						if event.key == pygame.K_e:
							active[0] = 2
						if event.key == pygame.K_r:
							active[0] = 3
						if event.key == pygame.K_t:
							active[0] = 4
						if event.key == pygame.K_y:
							active[0] = 5
						if event.key == pygame.K_u:
							active[0] = 6
						if event.key == pygame.K_i:
							active[0] = 7

						if event.key == pygame.K_w:
							active[2] = 0
						if event.key == pygame.K_x:
							active[2] = 1
						if event.key == pygame.K_c:
							active[2] = 2
						if event.key == pygame.K_v:
							active[2] = 3
						if event.key == pygame.K_b:
							active[2] = 4
						if event.key == pygame.K_n:
							active[2] = 5
						if event.key == 44:
							active[2] = 6
						if event.key == 59:
							active[2] = 7

						image_text = police.render( str(filtre_actuel+1),1,(255,0,0),(0,0,0))
			else: #affichage du choix des couleurs ==================================================
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_BACKSPACE:

							if mode[filtre_actuel] == 0: # mode gradient en fct de la freq du max d'amplitude
								nn = len(colors)
								if nn > 1:
									defin[filtre_actuel] = True
									color_freq[filtre_actuel] = blend_palette(colors, n_colors=N, as_cmap=False, input='rgb')
								elif nn == 1:
									defin[filtre_actuel] = True
									color_freq[filtre_actuel] = [colors[0] for _ in range(N)]
							elif mode[filtre_actuel] == 1:
								nn = len(colors)
								if nn > 1:
									defin[filtre_actuel] = True
									color_ampli[filtre_actuel] = blend_palette(colors, n_colors=NBS_COLOR, as_cmap=False, input='rgb')
								elif nn == 1:
									defin[filtre_actuel] = True
									color_ampli[filtre_actuel] = [colors[0] for _ in range(NBS_COLOR)]




							affiche_main = True
							
					if event.type == pygame.MOUSEBUTTONDOWN:
						x_pos,y_pos = pygame.mouse.get_pos()
						if  (370 < x_pos <= 400) and (0 <= y_pos <= 360):
							hu = y_pos/360
							sel_hu = True
							for x in range(360):
								for y in range(360):
									r,g,b = colorsys.hsv_to_rgb(hu, x/360, y/360)
									screen.set_at((x, y),(int(r*250),int(g*250),int(b*250)) )
						elif (0 <= x_pos <= 360) and (0 <= y_pos <= 360):
							if sel_hu:
								colors.append(colorsys.hsv_to_rgb(hu, x_pos/360, y_pos/360))
				
				pygame.display.flip()

## calcul de défilement ===================================================================
			jj = False
			if time.time() - (t1+ (time_ct*inter)) >= inter:
				
				if time_ct % (self.dure_bloc*self.hauteur_barre) == 0:
					
					if start:
						th = threading.Thread(target=Dj.create_display_bloc,args=(self,cpt_bloc,lock,))
						th.start()
						cpt_bloc += 1
						start = False
					else:
						if bb1:
							th.join()
							sur1 = SUR.copy()
							pos1 = pos2 + pas_coord
							th = threading.Thread(target=Dj.create_display_bloc,args=(self,cpt_bloc,lock,))
							cpt_bloc += 1
							th.start()
							bb1 = False
							jj = True
						else:
							th.join()
							sur2 = SUR.copy()
							pos2 = pos1 + pas_coord
							th = threading.Thread(target=Dj.create_display_bloc,args=(self,cpt_bloc,lock,))
							cpt_bloc += 1
							th.start()
							bb1 = True
							jj = True
				time_ct += 1
				
			if (time.time() - t2) >= (DURE / self.size_time):
				#t3 = time.time()
				tps_i += 1
				t2 += (DURE/self.size_time)
				if tps_i % 3 == 0: # parametrer la résolution !
					freq_max = [0,0,0,0,0,0,0,0]
					gg = [False,False,False,False,False,False,False,False]
					for i in range(8):
						if defin[i]:
							moy = 0
							mm = -1000
							for j in range(g_filte[i]//self.largeur_pix , d_filtre[i]//self.largeur_pix+1):
								moy += self.S[j,tps_i]
								if self.S[j,tps_i] >= mm:
									mm = self.S[j,tps_i]
									freq_max[i] = j
							moy = moy / ( (d_filtre[i]//self.largeur_pix) - (g_filte[i]//self.largeur_pix) + 1)
							if moy >= cap_filtre[i]:
								gg[i] = True

							ind_col[i] = int( (moy-self.bruit)/MAX * NBS_COLOR  )

					# affichage led ==================
				
					# 1er led forte
					if gg[active[0]]:
						black1 = False
						if (mode[active[0]] == 0): #mode 0 
							rrr = freq_max[active[0]] - (g_filte[active[0]]//self.largeur_pix)
							conn.write((str(int(color_freq[active[0]][rrr][0]*255))+"a"+str(int(color_freq[active[0]][rrr][1]*255))+"a"+str(int(color_freq[active[0]][rrr][2]*255))).encode(encoding="ascii")) 
						elif (mode[active[0]] == 1): #mode 1
							conn.write((str(int(color_ampli[ind_col[active[0]]][0]*255))+"a"+str(int(color_ampli[ind_col[active[0]]][1]*255))+"a"+str(int(color_ampli[ind_col[active[0]]][2]*255))).encode(encoding="ascii")) 
					else:
						if not black1:
							black1 = True
							conn.write((str(0)+"a"+str(0)+"a"+str(0)).encode(encoding="ascii")) 
					
					# 2 eme led forte 
					if gg[active[2]]:
						black2 = False
						if (mode[active[2]] == 0): #mode 0 
							rrr = freq_max[active[1]] - (g_filte[active[2]]//self.largeur_pix)
							conn.write((str(int(color_freq[active[2]][rrr][0]*255))+"b"+str(int(color_freq[active[2]][rrr][1]*255))+"b"+str(int(color_freq[active[2]][rrr][2]*255))).encode(encoding="ascii")) 
						elif (mode[active[2]] == 1): #mode 1
							conn.write((str(int(color_ampli[ind_col[active[2]]][0]*255))+"b"+str(int(color_ampli[ind_col[active[2]]][1]*255))+"b"+str(int(color_ampli[ind_col[active[2]]][2]*255))).encode(encoding="ascii")) 
					else:
						if not black2:
							black2 = True
							conn.write((str(0)+"b"+str(0)+"b"+str(0)).encode(encoding="ascii"))
					
					# 3 eme led nul 
					if gg[active[1]]:
						black3 = False
						if (mode[active[1]] == 0): #mode 0 
							rrr = freq_max[active[1]] - (g_filte[active[1]]//self.largeur_pix)
							conn2.write((str(int(color_freq[active[1]][rrr][0]*255))+"a"+str(int(color_freq[active[1]][rrr][1]*255))+"a"+str(int(color_freq[active[1]][rrr][2]*255))).encode(encoding="ascii")) 
						elif (mode[active[1]] == 1): #mode 1
							conn2.write((str(int(color_ampli[ind_col[active[1]]][0]*255))+"a"+str(int(color_ampli[ind_col[active[1]]][1]*255))+"a"+str(int(color_ampli[ind_col[active[1]]][2]*255))).encode(encoding="ascii")) 
					else:
						if not black3:
							black3 = True
							conn2.write((str(0)+"a"+str(0)+"a"+str(0)).encode(encoding="ascii"))
			
			if affiche_main:		
				screen.fill((0,0,0))
				screen.blit(sur1,(0,pos1-time_ct))
				screen.blit(sur2,(0,pos2-time_ct))
				pygame.draw.line(screen,(250,0,0),(g_filte[filtre_actuel],0) , (d_filtre[filtre_actuel],0),width=3)
				screen.blit(image_text,(0,0))
				screen.blit(sur_color,(0,SIZEy-PALETTE_SIZE))
				bar = pygame.Rect(cap_filtre[filtre_actuel]*x_inter*NBS_COLOR/MAX,SIZEy-20,2,20)
				pygame.draw.rect(screen,(250,0,0),bar)
				if x_prec != None:
					car = pygame.Rect(0,SIZEy-PALETTE_SIZE-20,20,20)
					pygame.draw.rect(screen,(0,250,0),car)
				for i in range(8):
					if gg[i]:
						if mode[i] == 0: # mode 0
							rrr = freq_max[i] - (g_filte[i]//self.largeur_pix)
							pygame.draw.rect(screen,(int(color_freq[i][rrr][0]*255),int(color_freq[i][rrr][1]*255),int(color_freq[i][rrr][2]*255)),carre_cot[i])
						elif mode[i] == 1: # mode 1
							pygame.draw.rect(screen,(int(color_ampli[ind_col[i]][0]*255),int(color_ampli[ind_col[i]][1]*255),int(color_ampli[ind_col[i]][2]*255)),carre_cot[i])
					else:
						pygame.draw.rect(screen,(0,0,0),carre_cot[i])
				for j in range(3):
					if gg[active[j]]:
						if mode[active[j]] == 0: #mode0
							rrr = freq_max[active[j]] - (g_filte[active[j]]//self.largeur_pix)
							pygame.draw.rect(screen,(int(color_freq[active[j]][rrr][0]*255),int(color_freq[active[j]][rrr][1]*255),int(color_freq[active[j]][rrr][2]*255)),carre_bas[j])
						elif mode[active[j]] == 1: # mode1
							pygame.draw.rect(screen,(int(color_ampli[ind_col[active[j]]][0]*255),int(color_ampli[ind_col[active[j]]][1]*255),int(color_ampli[ind_col[active[j]]][2]*255)),carre_bas[j])


				pygame.display.flip()	
			

ob = Dj()
ob.load_music(MUS)
ob.main_boucle()