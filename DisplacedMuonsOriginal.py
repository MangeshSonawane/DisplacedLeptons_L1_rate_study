#! /usr/bin/env python

## **************************************************************** ##
##  Look at properties of displaced muons from Kalman algo in BMTF  ##
## **************************************************************** ##

import os, sys
from math import *
from array import array

import ROOT as R
R.gROOT.SetBatch(False)  ## Don't print histograms to screen while processing

style1 = R.TStyle("style1", "For Histograms")
style1.SetLineWidth(2)
style1.SetOptStat(0)

R.gROOT.SetStyle("style1")

PRT_EVT  = 10000	 	## Print every Nth event
MAX_EVT  = 40000	## Number of events to process
VERBOSE  = False	## Verbose print-out

scale = [1., 1., 2544*11246., 1.]

def getPhi(globalPhiHw) :
    phi = globalPhiHw/287.5*pi if globalPhiHw<287.5 else \
                 (globalPhiHw-575.)/287.5*pi
    return phi

def getGenEtaPhi(Gen_br, i, mutype):
	if mutype == 1 : return getGenEtaPhiBarrel(Gen_br, i)
	elif mutype == 3 : return getGenEtaPhiEndcap(Gen_br, i)
	elif mutype == 2 : return Gen_br.partEta[i], Gen_br.partPhi[i]
	else  : return False, False

def getGenEtaPhiBarrel(Gen_br, i):

	eta 	= float(Gen_br.partEta[i])
	vx	= float(Gen_br.partVx[i])
	vy	= float(Gen_br.partVy[i])
	vz	= float(Gen_br.partVz[i])
	phi 	= float(Gen_br.partPhi[i])

	Lxy = sqrt(float(Gen_br.partVx[i])**2 + float(Gen_br.partVy[i])**2)	

	r = (490. - Lxy)
	z = r*sinh(eta)

	zStar = vz + z
	xStar = vx + r*cos(phi)
	yStar = vy + r*sin(phi)
 
	rStar = sqrt(xStar**2 + yStar**2)
	
	GenEta = asinh(zStar/490.)
	
	if (xStar >= 0) : GenPhi = atan(yStar/xStar)
      	elif (yStar >= 0 and xStar < 0) : GenPhi = pi + atan(yStar/xStar)
      	elif (yStar <= 0 and xStar < 0) : GenPhi = atan(yStar/xStar) - pi 	
	
	return GenEta, GenPhi

def IsinacceptBarrel(Gen_br, i):

	vx = float(Gen_br.partVx[i])
	vy = float(Gen_br.partVy[i])
	vz = float(Gen_br.partVz[i])

	eta = float(Gen_br.partEta[i])
	
	if abs(vz) >= 650. : return False
	
	Lxy = sqrt(vx**2 + vy**2)
	if Lxy > 490. : return False

	maxeta = -log(tan(0.5*atan((700.-Lxy)/(650.-vz))))
	mineta = -log(tan (0.5*(pi-atan((700.-Lxy)/(650.+vz)))))

	if eta >= maxeta or eta <= mineta : return False
	
	return True

def getGenEtaPhiEndcap(Gen_br, i):				
	
	z_ME2 	= 800.
	eta 	= float(Gen_br.partEta[i])
	phi 	= float(Gen_br.partPhi[i])
	z	= float(Gen_br.partVz[i])	

	if (eta > 0) 	: r = abs(z_ME2 - z)/abs(sinh(eta))
	else	    	: r = abs(- z_ME2 - z)/abs(sinh(eta))

	xStar = float(Gen_br.partVx[i]) + r*cos(phi)
	yStar = float(Gen_br.partVy[i]) + r*sin(phi)
	rStar = sqrt(xStar**2 + yStar**2)

	GenEta	= asinh(z_ME2/rStar)*(eta/abs(eta))

	if (xStar >= 0) : GenPhi = atan(yStar/xStar)
      	elif (yStar >= 0 and xStar < 0) : GenPhi = pi + atan(yStar/xStar)
      	elif (yStar <= 0 and xStar < 0) : GenPhi = atan(yStar/xStar) - pi 	

	return GenEta, GenPhi

def IsinacceptEndcap(Gen_br, i):

	vx = float(Gen_br.partVx[i])
	vy = float(Gen_br.partVy[i])
	vz = float(Gen_br.partVz[i])

	if abs(vz) >=800. : return False

	Lxy = sqrt(vx**2 + vy**2)
	if Lxy > 490. : return False

	eta, phi = getGenEtaPhiEndcap(Gen_br, i)

	if abs(eta) <= 1.245 : return False
	if abs(eta) >= 2.450 : return False	

	return True

def getDxy(vx, vy, phi):
	return abs(vx*sin(phi)-vy*cos(phi))


##################################################################################################################


def main():

    print '\nInside DisplacedMuons\n'
    evtclass = ["signal_1500", "signal_3000","NuGun","DisplacedMuGun"]
    evtclassid = 1
    inputdir = ['/eos/user/s/sonawane/temp/L1Ntuples/signal_1500_tuples/',
		'/eos/user/s/sonawane/temp/L1Ntuples/signal_tuples/ntuples_01_07_21/backup/',
		'/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/bundocka/condor/reHcalTP_Nu_11_2_105p20p1_1623921599/',
		'/eos/user/s/sonawane/temp/L1Ntuples/Displaced_mu_gun_tuples/ntuples_16_06_21/']

    workdir = '/afs/cern.ch/user/s/sonawane/L1T/L1studies/L1_scripts_Alberto/L1RunIII/macros/'
    in_file_names = []

    if evtclassid == 3:
	for s in ['DisplacedMuGun_Pt2to10_11_2_X_1623847533/', 'DisplacedMuGun_Pt10to30_11_2_X_1623847663/', 'DisplacedMuGun_Pt30to100_11_2_X_1623847721/']:
#	for s in ['MuGun_Pt2to10_Nu_11_2_X_1623157277/']:
		ntupledir = inputdir[evtclassid]+s
		for i in range(23) :
        		path = ntupledir+str(i)+".root"
        		if not os.path.exists(path): continue
			in_file_names.append(path)
			
    elif evtclassid == 1:
	filestr = ['HTo2LongLivedTo4mu_MH-125_MFF-12_CTau-900mm_11_2_X_1625152032/', 'HTo2LongLivedTo4mu_MH-125_MFF-25_CTau-1500mm_11_2_X_1625152298/', 'HTo2LongLivedTo4mu_MH-125_MFF-50_CTau-3000mm_11_2_X_1623847924/']
	for l in range(2,3) :
		s = filestr[l]
		ntupledir = inputdir[evtclassid]+s
		for i in range(14) :
        		path = ntupledir+str(i)+".root"
        		if not os.path.exists(path): continue
			in_file_names.append(path)

    else:
	for i in range(14):
	        path = inputdir[evtclassid]+str(i)+".root"
       	 	if not os.path.exists(path): continue
		in_file_names.append(path)
    
    if not os.path.exists(workdir+'plots'): os.makedirs(workdir+'plots')

    MU_QLTY_SNGL = [12, 13, 14, 15]
    MU_QLTY_DBLE = [8, 9, 10, 11, 12, 13, 14, 15]

#	For testing
#    in_file_names=['/afs/cern.ch/user/s/sonawane/L1T/L1studies/L1_scripts_Alberto/L1RunIII/test/L1Ntuple.root']

    out_file_str = 'DisplacedMuons_'+evtclass[evtclassid]
    out_file_str += ('_%dk' % (MAX_EVT / 1000))
    out_file = R.TFile(workdir+'plots/'+out_file_str+'.root','recreate')

    chains = {}
    chains['Evt'] = []  ## Event info
    chains['Unp'] = []  ## Unpacked legacy BMTF
    chains['Emu'] = []  ## Emulated Kalman BMTF
    chains['EmuK'] = []  ## Emulated Kalman BMTF
    chains['EmuE'] = []  ## Emulated Kalman BMTF
    chains['uGT'] = []  ## Global Trigger
    chains['Gen'] = []  ## Generator information

    chains['Evt'].append( R.TChain('l1EventTree/L1EventTree') )
    chains['Unp'].append( R.TChain('l1UpgradeTfMuonTree/L1UpgradeTfMuonTree') )
    chains['Emu'].append( R.TChain('l1UpgradeTfMuonEmuTree/L1UpgradeTfMuonTree') )
    chains['EmuK'].append( R.TChain('l1UpgradeTfMuonEmuTree/L1UpgradeTfMuonTree') )
    chains['EmuE'].append( R.TChain('l1UpgradeTfMuonEmuTree/L1UpgradeTfMuonTree') )
    chains['uGT'].append( R.TChain('l1UpgradeEmuTree/L1UpgradeTree') )
    chains['Gen'].append( R.TChain('l1GeneratorTree/L1GenTree') )

    for i in range(len(in_file_names)):
        print 'Adding file %s' % in_file_names[i]
        chains['Evt'][0].Add( in_file_names[i] )
        chains['Unp'][0].Add( in_file_names[i] )
        chains['Emu'][0].Add( in_file_names[i] )
        chains['EmuK'][0].Add( in_file_names[i] )
        chains['EmuE'][0].Add( in_file_names[i] )
        chains['uGT'][0].Add( in_file_names[i] )
        chains['Gen'][0].Add( in_file_names[i] )


    ###################
    ### Book histograms
    ###################

    pt_bins  = [150, 0, 300]
    q_pt_bins  = [100, -0.2, 0.2]
#    chi_bins = [100, 0, 100]
    dxy_bins = [40,   0, 200]
    vxyz_bins = [200,   -200, 200]
    lxy_bins = [30,   0, 150]
    phi_bins = [80, -4.,4.]
    eta_bins = [30, -3., 3.]
    dphi_bins = [40, 0., 4.]
    deta_bins = [30, 0., 3.]
#    Vx_bins  = [100,-50, 50]
#    phi_bins = [80, -4, 4]
    EC_eta_bins = [-3., -2.5, -2.1, -1.6, -1.2, 1.2, 1.6, 2.1, 2.5, 3.]

### Single Muon Efficiencies ########

    h_pt_blank = R.TH1F('h_pt_blank', 'Blank Gen Pt', pt_bins[0], pt_bins[1], pt_bins[2])
    h_dxy_blank = R.TH1F('h_dxy_blank', 'Blank Gen Dxy', dxy_bins[0], dxy_bins[1], dxy_bins[2])
    h_EC_eta_blank = R.TH1F('h_EC_eta_blank', 'Blank Gen Eta (Endcap)', len(EC_eta_bins)-1, array('d',EC_eta_bins))

    

#Event counters

    GenMuevt_count 		= 0
    
    GenMuCount 			= 0
    GenMuinAcc			= 0

    EmuMuevt_count	 	= 0
    EmuMus_count		= 0
    EmuMus_unique_count 	= 0

    matched_gen_mu_count	= 0
    matched_gen_mu_evt		= 0

    mismatch_evt		= 0

    iEvt 			= 0 

#    Efficiencies
    Baseline_Run_2_num		= 0
    Baseline_Run_2_den		= 0
    Den2 			= 0
    Den3			= 0

    Extended_Run_2_num		= 0
    Extended_Run_2A_num		= 0
    Extended_Run_2B_num		= 0

    Baseline_Run_2_UPT_BMTF_num	= 0
    Baseline_Run_2_UPT_num  	= 0
    Baseline_Run_2_UPT_dxy1_num	= 0

    Extended_Run_2_UPT_dxy1_num = 0
    Extended_Run_2_UPT_num = 0

    ##### Dimuon counters #####
   
    GenDimu_Evt = 0

    print '\nEntering loop over chains'
    for iCh in range(len(chains['Emu'])):

        if iEvt >= MAX_EVT: break

        ## Faster tecnhique, inspired by https://github.com/thomreis/l1tMuonTools/blob/master/L1Analysis.py
        Evt_br = R.L1Analysis.L1AnalysisEventDataFormat()
        Unp_br = R.L1Analysis.L1AnalysisL1UpgradeTfMuonDataFormat()
        EmuK_br = R.L1Analysis.L1AnalysisL1UpgradeTfMuonDataFormat()
        EmuE_br = R.L1Analysis.L1AnalysisL1UpgradeTfMuonDataFormat()
        uGT_br = R.L1Analysis.L1AnalysisL1UpgradeDataFormat()
        Gen_br = R.L1Analysis.L1AnalysisGeneratorDataFormat()
#        Kmt_br = R.L1Analysis.L1AnalysisBMTFOutputDataFormat()

        chains['Evt'][iCh].SetBranchAddress('Event',               R.AddressOf(Evt_br))
        chains['Unp'][iCh].SetBranchAddress('L1UpgradeBmtfMuon',   R.AddressOf(Unp_br))
        chains['EmuK'][iCh].SetBranchAddress('L1UpgradeKBmtfMuon', R.AddressOf(EmuK_br))
        chains['EmuE'][iCh].SetBranchAddress('L1UpgradeEmtfMuon',  R.AddressOf(EmuE_br))
        chains['uGT'][iCh].SetBranchAddress('L1Upgrade',  	   R.AddressOf(uGT_br))
        chains['Gen'][iCh].SetBranchAddress('Generator',           R.AddressOf(Gen_br))
#        chains['Emu'][iCh].SetBranchAddress('L1UpgradeBmtfOutput', R.AddressOf(Kmt_br))

	

        print '\nEntering loop over events for chain %d' % iCh
        for jEvt in range(chains['Emu'][iCh].GetEntries()):

            if iEvt >= MAX_EVT: break

	    iEvt +=1

            if iEvt % PRT_EVT is 0: print '\nEvent # %d (%dth in chain)' % (iEvt, jEvt+1)

            chains['Evt'][iCh].GetEntry(jEvt)
            chains['Unp'][iCh].GetEntry(jEvt)
            chains['EmuK'][iCh].GetEntry(jEvt)
            chains['EmuE'][iCh].GetEntry(jEvt)
            chains['uGT'][iCh].GetEntry(jEvt)
            chains['Gen'][iCh].GetEntry(jEvt)

            # ## Use these lines if you don't explicitly define the DataFormat and then do SetBranchAddress above
            # Evt_br = chains['Evt'][iCh].Event
            # Unp_br = chains['Unp'][iCh].L1UpgradeBmtfMuon
            # Emu_br = chains['Emu'][iCh].L1UpgradeBmtfMuon

            if iEvt % PRT_EVT is 0: print '  * Run %d, LS %d, event %d' % (int(Evt_br.run), int(Evt_br.lumi), int(Evt_br.event))

            nUnpMu = int(Unp_br.nTfMuons)
            nEmuKMu = int(EmuK_br.nTfMuons)
            nEmuEMu = int(EmuE_br.nTfMuons)
            nuGTMu = int(uGT_br.nMuons)
	    nGenPart = int(Gen_br.nPart)
#            nKmtMu = int(Kmt_br.nTrks)
	    
	    ##########################
            ###  Index containers  ###
            ##########################
	    
  	    GenMus			=[]
	    GenMus_acc	 		=[]
	    EmuMus			=[]
	    EmuMus_unique		=[]
	    GenMuPt_acc			=[]

	    EmuKMus			=[]
	    EmuEMus			=[]
	    EmuKMus_unique		=[]
	    EmuEMus_unique		=[]
	
	    #########################################
            ###  Generator information for muons  ###
            #########################################

	    for i in range(nGenPart):
	
		if (abs(Gen_br.partId[i])!=13): continue
#		if (Gen_br.partStat[i]!=1): continue

		### weighting MuGun events ###
		
		weight = 1.

#		if abs(float(Gen_br.partVx[i])) > 120. 	: continue
#		if abs(float(Gen_br.partVy[i])) > 120. 	: continue
#		if abs(float(Gen_br.partVz[i])) > 100. 	: continue
#		if float(Gen_br.partPt[i]) < 2		: continue
	
		if (Gen_br.partParent[i]!=6000113): continue

		GenMus.append(i)

		if IsinacceptBarrel(Gen_br, i) : MuType = 1 
		elif IsinacceptEndcap(Gen_br, i) : MuType = 3
		else : continue 	

		GenMus_acc.append([i, MuType])

                gen_eta, gen_phi = getGenEtaPhi(Gen_br, i, MuType)
		GenDxy  = getDxy(float(Gen_br.partVx[i]), float(Gen_br.partVy[i]), float(Gen_br.partPhi[i]))
                z0      = float(Gen_br.partVz[i])
		ptgen 	= float(Gen_br.partPt[i])
		
		GenMuPt_acc.append([Gen_br.partPt[i], i, MuType])

	    GenMuPt_acc.sort(reverse=True)

            #################################
            ###  Emulated uGT muons  ###
            #################################

            for i in range(nuGTMu):
                BX      = int(uGT_br.muonBx[i])
                                
                if (BX  !=  0): continue
#                if (qual < 11): continue

		EmuMus.append(i)

	    Eta_phi = []

            for i in EmuMus :

                pt1  = float(uGT_br.muonEt[i])
                eta1 = float(uGT_br.muonEta[i])
                phi1 = float(uGT_br.muonPhi[i])

                ep = [eta1, phi1]

                pt_i = [pt1, i]

                ptmax = pt1

                if ep in Eta_phi : continue

                Eta_phi.append(ep)

                for j in EmuMus :
                        if j <= i : continue

                        pt2 = float(uGT_br.muonEt[j])
                        eta2 = float(uGT_br.muonEta[j])
                        phi2 = float(uGT_br.muonPhi[j])

                        if eta1==eta2 and phi1==phi2 :
                                if pt2 > ptmax :
                                        ptmax = pt2
                                        pt_i = [pt2, j]

		EmuMus_unique.append(pt_i[1])

            #################################
            ###  Emulated kBMTF muons  ###
            #################################

            for i in range(nEmuKMu):
                BX      = int(EmuK_br.tfMuonBx[i])

                if (BX  !=  0): continue
#               if (qual < 11): continue
		
		EmuKMus.append(i)

	    Eta_phi = []

            for i in EmuKMus :

                pt1  = float(EmuK_br.tfMuonHwPt[i]-1.)*0.5
                eta1 = float(EmuK_br.tfMuonHwEta[i])*0.010875
                phi1 = getPhi(float(EmuK_br.tfMuonGlobalPhi[i]))

                ep = [eta1, phi1]

                pt_i = [pt1, i]

                ptmax = pt1

                if ep in Eta_phi : continue

                Eta_phi.append(ep)

                for j in EmuKMus :
                        if j <= i : continue

                        pt2 = float(EmuK_br.tfMuonHwPt[j]-1.)*0.5
                        eta2 = float(EmuK_br.tfMuonHwEta[j])*0.010875
                        phi2 = getPhi(float(EmuK_br.tfMuonGlobalPhi[j]))

                        if eta1==eta2 and phi1==phi2 :
                                if pt2 > ptmax :
                                        ptmax = pt2
                                        pt_i = [pt2, j]

                EmuKMus_unique.append(pt_i[1])

            #################################
            ###  Emulated EMTF muons  ###
            #################################

            for i in range(nEmuEMu):
                BX      = int(EmuE_br.tfMuonBx[i])
                qual    = int(EmuE_br.tfMuonHwQual[i])
                ptVtx   = float(EmuE_br.tfMuonHwPt[i]-1.)*0.5  ## Vertex-constrained (standard) pT is stored in 0.5 GeV steps
                ptDisp  = float(EmuE_br.tfMuonHwPtUnconstrained[i]-1.)  ## Vertex-unconstrained pT

		mu1 = R.TLorentzVector()
		mu1.SetPtEtaPhiM(ptDisp, float(EmuE_br.tfMuonHwEta[i])*0.010875, getPhi(float(EmuE_br.tfMuonGlobalPhi[i])), 105.7e-3)
		eta = mu1.Eta()
		phi = mu1.Phi()
                                
                if (BX  !=  0): continue
#               if (qual < 11): continue

		savemuindex = i
		ptmax = -1.
		
		for j in range(i+1, nEmuEMu):
			mu2 = R.TLorentzVector()
			mu2.SetPtEtaPhiM(float(EmuE_br.tfMuonHwPtUnconstrained[j]-1.), float(EmuE_br.tfMuonHwEta[j]*0.010875), getPhi(float(EmuE_br.tfMuonGlobalPhi[j])), 105.7e-3)
			pt_j   = max(float(EmuE_br.tfMuonHwPtUnconstrained[j]-1.), float(EmuE_br.tfMuonHwPt[j]-1.)*0.5)
			eta_j  = mu2.Eta()
			phi_j  = mu2.Phi()

			if (eta == eta_j and phi == phi_j):
				
				if (ptmax < pt_j): 
					ptmax = pt_j
					savemuindex = j
				else :	savemuindex = i

		if i != savemuindex: continue
	
		EmuEMus_unique.append(i)

	    # Better matching subroutine

	    dR_list=[]
	    dR_list_corr=[]

	    EMTF_dR_list=[]
	    kBMTF_dR_list=[]

	    for el in GenMus_acc:
		
		i = el[0]
		mutype = el[1]
		
		GenMuCorr = R.TLorentzVector()
		temp_eta, temp_phi = getGenEtaPhi(Gen_br, i, mutype)
		GenMuCorr.SetPtEtaPhiM(float(Gen_br.partPt[i]), temp_eta, temp_phi, 105.7e-3)
		eta1corr = GenMuCorr.Eta()
		phi1corr = GenMuCorr.Phi()

		for j in EmuMus_unique:
			EmuMuvec = R.TLorentzVector()
			EmuMuvec.SetPtEtaPhiM(float(uGT_br.muonEtUnconstrained[j]), float(uGT_br.muonEta[j]), float(uGT_br.muonPhi[j]), 105.7e-3)
	
			dR_corr = EmuMuvec.DeltaR(GenMuCorr)
			if dR_corr < 0.6: dR_list_corr.append([dR_corr, i, j, mutype])

		for j in EmuKMus_unique:
			EmuMuvec = R.TLorentzVector()
			EmuMuvec.SetPtEtaPhiM(float(EmuK_br.tfMuonHwPtUnconstrained[j]-1.), float(EmuK_br.tfMuonHwEta[j])*0.010875, getPhi(float(EmuK_br.tfMuonGlobalPhi[j])), 105.7e-3)
	
			dR_corr = EmuMuvec.DeltaR(GenMuCorr)
			if dR_corr < 0.6: kBMTF_dR_list.append([dR_corr, i, j, mutype])

		for j in EmuEMus_unique:
			EmuMuvec = R.TLorentzVector()
			EmuMuvec.SetPtEtaPhiM(float(EmuE_br.tfMuonHwPtUnconstrained[j]-1.), float(EmuE_br.tfMuonHwEta[j])*0.010875, getPhi(float(EmuE_br.tfMuonGlobalPhi[j])), 105.7e-3)
	
			dR_corr = EmuMuvec.DeltaR(GenMuCorr)
			if dR_corr < 0.6: EMTF_dR_list.append([dR_corr, i, j, mutype])

#	    mismatch_flag = False

	    dR_list = dR_list_corr

	    if len(dR_list):

		    dR_list.sort()


	    k = False
	    if len(dR_list): k = True
	    i = 0
	    while k:
		k = False
		idx1 = dR_list[i][1]
		idx2 = dR_list[i][2]
		j = i+1
		while j < len(dR_list):
			idx_1  = dR_list[j][1]
			idx_2  = dR_list[j][2]

			if idx1 == idx_1 or idx2 == idx_2: del dR_list[j]
			else : j +=1
	  	i +=1
		if i < len(dR_list): 
			k = True

### kBMTF_dR_list cleaning
	    if len(kBMTF_dR_list):

		    kBMTF_dR_list.sort()

		    k = True 
		    i = 0
		    while k:
			k = False
			idx1 = kBMTF_dR_list[i][1]
			idx2 = kBMTF_dR_list[i][2]
			j = i+1
			while j < len(kBMTF_dR_list):
				idx_1  = kBMTF_dR_list[j][1]
				idx_2  = kBMTF_dR_list[j][2]
	
				if idx1 == idx_1 or idx2 == idx_2: del kBMTF_dR_list[j]
				else : j +=1
		  	i +=1
			if i < len(kBMTF_dR_list): 
				k = True

### EMTF_dR_list cleaning
	    if len(EMTF_dR_list):

		    EMTF_dR_list.sort()

		    k = True 
		    i = 0
		    while k:
			k = False
			idx1 = EMTF_dR_list[i][1]
			idx2 = EMTF_dR_list[i][2]
			j = i+1
			while j < len(EMTF_dR_list):
				idx_1  = EMTF_dR_list[j][1]
				idx_2  = EMTF_dR_list[j][2]
	
				if idx1 == idx_1 or idx2 == idx_2: del EMTF_dR_list[j]
				else : j +=1
		  	i +=1
			if i < len(EMTF_dR_list): 
				k = True


####### Dxy turnon for kBMTF, GMT and EMTF #######

####### Efficiencies for EMTF ############
		
#	    for i in range(len(dR_list)) :
#		Emu_idx = dR_list[i][2]
#		Gen_idx = dR_list[i][1]
#		L1Dxy	= float(uGT_br.muonDxy[Emu_idx])
#		GenDxy  = getDxy(float(Gen_br.partVx[Gen_idx]), float(Gen_br.partVy[Gen_idx]), float(Gen_br.partPhi[Gen_idx]))
#		z0 	= float(Gen_br.partVz[Gen_idx])
#		ptgen 	= float(Gen_br.partPt[Gen_idx])
#		dR	= dR_list[i][0] 
#		ptVtx 	= float(uGT_br.muonEt[Emu_idx])
#		ptDisp 	= float(uGT_br.muonEtUnconstrained[Emu_idx])
#		gen_eta, gen_phi = getGenEtaPhi(Gen_br, Gen_idx, mutype)
#		eta 	= float(uGT_br.muonEta[Emu_idx])

#		qual 	= int(uGT_br.muonQual[Emu_idx])
		

##################################################

##################### Efficiency for Dimuons ###############3

	    Dimus_acc = []
	    
	    if len(GenMus) >= 2 :
		for i in range(len(GenMus)):
			idx1 = GenMus[i]
			vx1 = float(Gen_br.partVx[idx1])
			vy1 = float(Gen_br.partVy[idx1])
			vz1 = float(Gen_br.partVz[idx1])

			pt1 = float(Gen_br.partPt[idx1])

			for j in range(i+1, len(GenMus)):
				idx2 = GenMus[j]
				vx2 = float(Gen_br.partVx[idx2])
				vy2 = float(Gen_br.partVy[idx2])
				vz2 = float(Gen_br.partVz[idx2])
				pt2 = float(Gen_br.partPt[idx2])

				if vx1==vx2 and vy1==vy2 and vz1==vz2:
	
#					if pt1 <=23. or pt2 <=23. : continue
#					lxy = sqrt(vx1**2 + vy1**2)
#					if lxy < 60.   : continue
			
					if pt1 >= pt2 	:	el = [idx1, idx2]
					else 		:	el = [idx2, idx1]
					Dimus_acc.append(el)


	    Baseline_Run_2_den +=len(Dimus_acc)

	    if len(Dimus_acc) :

#	Debug block
#
#		print 'Dimus in acceptance: ', Dimus_acc
#		if len(Dimus_acc) > 2 : 
#			for k in range(len(Dimus_acc)):
#				idx1 = Dimus_acc[k][0]
#				idx2 = Dimus_acc[k][1]
#				v1 = [float(Gen_br.partVx[idx1]),float(Gen_br.partVy[idx1]),float(Gen_br.partVz[idx1])]
#				v2 = [float(Gen_br.partVx[idx2]),float(Gen_br.partVy[idx2]),float(Gen_br.partVz[idx2])]
#				print 'Muon Coordinates:'
#				print 'Idx1 : ', idx1, '\t', v1
#				print 'Idx2 : ', idx2, '\t', v2


	    	matched_dimus=[]

		GenDimu_Evt +=1 
		for j in range(len(Dimus_acc)):
			temp = []
			for i in range(len(dR_list)):
				Gen_idx = dR_list[i][1]
				if Gen_idx in Dimus_acc[j] :
					el = [Gen_idx, dR_list[i][2]]
					if el not in temp:
						temp.append(el)
			if len(temp) == 2 : matched_dimus.append(temp)
			
#			idx1 = Dimus_acc[j][0]
#			idx2 = Dimus_acc[j][1]

		for dim_pair in matched_dimus:

			L1_DoubleMu_15_7_flag 			= False
			L1_DoubleMu0er1p5_SQ_dR_Max1p4_flag 	= False
  			L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag	= False		 
			L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag  = False

   			L1_DoubleMu_15_7_UPT_BMTF_flag		= False
   			L1_DoubleMu_15_7_UPT_flag		= False
			L1_DoubleMu_15_7_UPT_DXY1_flag		= False

                        genidx1 = dim_pair[0][0]
                        genidx2 = dim_pair[1][0]
                        emuidx1 = dim_pair[0][1]
                        emuidx2 = dim_pair[1][1]

			ptVtx1 = float(uGT_br.muonEt[emuidx1])
			ptVtx2 = float(uGT_br.muonEt[emuidx2])
			ptDisp1 = float(uGT_br.muonEtUnconstrained[emuidx1])
			ptDisp2 = float(uGT_br.muonEtUnconstrained[emuidx2])

			dxy1   = float(uGT_br.muonDxy[emuidx1])
			dxy2   = float(uGT_br.muonDxy[emuidx2])

			eta1   = float(uGT_br.muonEta[emuidx1])
			eta2   = float(uGT_br.muonEta[emuidx2])

			phi1   = float(uGT_br.muonPhi[emuidx1])
			phi2   = float(uGT_br.muonPhi[emuidx2])

			v1 = R.TLorentzVector()
			v2 = R.TLorentzVector()
		
			v1.SetPtEtaPhiM(ptVtx1, eta1, phi1, 0.)
			v2.SetPtEtaPhiM(ptVtx2, eta2, phi2, 0.)
			dR = v1.DeltaR(v2)

			ch1    = float(uGT_br.muonChg[emuidx1])
			ch2    = float(uGT_br.muonChg[emuidx2])

			pt1 = max(ptVtx1, ptVtx2)
			pt2 = min(ptVtx1, ptVtx2)
			ptdisp1 = max(ptDisp1, ptDisp2)
			ptdisp2 = min(ptDisp1, ptDisp2)

			qual1 = int(uGT_br.muonQual[emuidx1])
			qual2 = int(uGT_br.muonQual[emuidx2])


			if (qual1 in MU_QLTY_DBLE) and (qual2 in MU_QLTY_DBLE) :
				if pt1 >= 15. and pt2 >= 7. : L1_DoubleMu_15_7_flag = True
				
				if ptdisp1 >= 15. and ptdisp2 >= 7. and abs(eta1)<= 0.8 and abs(eta2) <= 0.8        		: L1_DoubleMu_15_7_UPT_BMTF_flag	= True
				if ptdisp1 >= 15. and ptdisp2 >= 7. 			       		: L1_DoubleMu_15_7_UPT_flag   		= True
				if ptdisp1 >= 15. and ptdisp2 >= 7. and dxy1 >= 1 and dxy2 >= 1		: L1_DoubleMu_15_7_UPT_DXY1_flag  	= True

			
			if (qual1 in MU_QLTY_SNGL) and (qual2 in MU_QLTY_SNGL) :
				if (ptVtx >= 0. and ptVtx2 >= 0.) and (abs(eta1) <= 1.506 and abs(eta2) <= 1.506):
                                        if (ch1*ch2 < 0 and dR <= 1.4)  : L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag = True

				if (ptVtx >= 4.5 and ptVtx2 >= 4.5) :
                                        if (ch1*ch2 < 0 and dR <= 1.2)  : L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag = True

	
			if L1_DoubleMu_15_7_flag : Baseline_Run_2_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag or L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag) : Extended_Run_2_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu_15_7_UPT_BMTF_flag) : Baseline_Run_2_UPT_BMTF_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu_15_7_UPT_flag) : Baseline_Run_2_UPT_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu_15_7_UPT_DXY1_flag) : Baseline_Run_2_UPT_dxy1_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag or L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag or L1_DoubleMu_15_7_UPT_DXY1_flag) :
				Extended_Run_2_UPT_dxy1_num += 1.
			if (L1_DoubleMu_15_7_flag or L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag or L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag) or (L1_DoubleMu_15_7_UPT_flag) : 
				Extended_Run_2_UPT_num += 1.
			
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4_flag) : Extended_Run_2A_num += 1.
			if L1_DoubleMu_15_7_flag or (L1_DoubleMu4p5_SQ_OS_dR_Max1p2_flag) : Extended_Run_2B_num += 1.
			
	
	    ##End of sub loop over Gen, Emu or Unp muons

#	    print "GenMus: ", len(GenMus)
#	    print "GenMusAcc: ", len(GenMus_acc)
#	    print "EmuMus: ", len(EmuMus)
#	    print "EmuMus unique: ", len(EmuMus_unique)
	
	    ###########################
            ###  Updating counters  ###
            ###########################
 	    
	    if len(GenMus) : GenMuevt_count +=1
	    GenMuCount += len(GenMus)
	    GenMuinAcc += len(GenMus_acc)

	    if len(EmuMus) : EmuMuevt_count +=1
	    EmuMus_count += len(EmuMus)

	    EmuMus_unique_count +=len(EmuMus_unique)

	    if len(dR_list) : matched_gen_mu_evt +=1

        ## End loop: for jEvt in range(chains['Unp'][iCh].GetEntries()):
    ## End loop: for iCh in range(len(chains['Unp'])):

    print '\nFinished loop over chains'

    out_file.cd()

    h_pt_blank.Write()
    h_EC_eta_blank.Write()
    h_dxy_blank.Write()


    out_file.Close()
    del chains

    print '\nWrote out file: plots/'+out_file_str+'.root'
    print '\n Events run over: ', iEvt

    print 'Event counter'
    print 'Total GenMus: ', GenMuCount
    print 'GenMus in Acceptance: ', GenMuinAcc
    print 'EmuMus passing qual: ', EmuMus_count
    print 'EmuMus passing qual and unique: ', EmuMus_unique_count
    
    print 'Mismatch between corr and uncorr Gen Muons matched to qual emus: ', mismatch_evt

    print 'Matched gen mus : ', matched_gen_mu_count
    print 'Events with matched gen Mus: ', matched_gen_mu_evt

    print 'Events with Gen Dimuons: ', GenDimu_Evt

    print "\n################################# Efficiencies ##################################\n"

    print "Dimuons : ", Baseline_Run_2_den*1.
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Baseline run 2 ", Baseline_Run_2_num, Baseline_Run_2_num*1./Baseline_Run_2_num, \
	Baseline_Run_2_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Extended run 2 ", Extended_Run_2_num*1., Extended_Run_2_num*1./Baseline_Run_2_num, \
	Extended_Run_2_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Extended run 2A ", Extended_Run_2A_num*1., Extended_Run_2A_num*1./Baseline_Run_2_num, \
	Extended_Run_2A_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Extended run 2B ", Extended_Run_2B_num*1., Extended_Run_2B_num*1./Baseline_Run_2_num, \
	Extended_Run_2B_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Baseline run 2 + Unconstrained BMTF ", Baseline_Run_2_UPT_BMTF_num*1., Baseline_Run_2_UPT_BMTF_num*1./Baseline_Run_2_num,\
	Baseline_Run_2_UPT_BMTF_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Baseline run 2 + Unconstrained ", Baseline_Run_2_UPT_num*1., Baseline_Run_2_UPT_num*1./Baseline_Run_2_num, \
	Baseline_Run_2_UPT_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Baseline run 2 + Unconstrained + DXY1", Baseline_Run_2_UPT_dxy1_num*1., Baseline_Run_2_UPT_dxy1_num*1./Baseline_Run_2_num,\
	Baseline_Run_2_UPT_dxy1_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Extended Run 2 + Unconstrained DXY1", Extended_Run_2_UPT_dxy1_num*1., Extended_Run_2_UPT_dxy1_num*1./Baseline_Run_2_num, \
	Extended_Run_2_UPT_dxy1_num*1./Extended_Run_2_num)
    print "%-50s : %.4f :\t%.4f :\t%.4f" %("Extended Run 2 + Unconstrained", Extended_Run_2_UPT_num*1., Extended_Run_2_UPT_num*1./Baseline_Run_2_num, \
	Extended_Run_2_UPT_num*1./Extended_Run_2_num)

    print "\n############################################## ##################################\n"

if __name__ == '__main__':
    main()



#                h_pt_displ_emu.Fill( min( max( ptDispl+0.01, pt_bins[1]+0.01), pt_bins[2]-0.01) )
#    h_pt_vtx_unp   = R.TH1F('h_pt_vtx_unp',   'Legacy BMTF vertex-constrained pT spectrum',         pt_bins[0], pt_bins[1], pt_bins[2])
#    h_pt_vtx_emu   = R.TH1F('h_pt_vtx_emu',   'Kalman BMTF vertex-constrained pT spectrum',         pt_bins[0], pt_bins[1], pt_bins[2])
#    h_phi_mu_emu   = R.TH1F('h_phi_mu_emu',   'Kalman BMTF muon Phi',         		phi_bins[0], phi_bins[1], phi_bins[2])
#    h_pt_displ_emu = R.TH1F('h_pt_displ_emu', 'Kalman BMTF non-vertex-constrained pT spectrum',     pt_bins[0], pt_bins[1], pt_bins[2])
#    h_pt_dxy_emu   = R.TH2F('h_pt_dxy_emu',   'Kalman BMTF non-vertex-constrained pT vs dxy',       pt_bins[0], pt_bins[1], pt_bins[2], dxy_bins[0], dxy_bins[1], dxy_bins[2])
#    h_pt_displ_kmt = R.TH1F('h_pt_displ_kmt', 'Internal Kalman non-vertex-constrained pT spectrum', pt_bins[0], pt_bins[1], pt_bins[2])
#    h_chi2_kmt = R.TH1F('h_chi2_kmt', 'Kalman BMTF track #chi^{2} distribution', chi_bins[0], chi_bins[1], chi_bins[2])

 #   h_Vx_gen = R.TH1F('h_Vx_gen', 'Generator level Vertex x coordinate',     Vx_bins[0], Vx_bins[1], Vx_bins[2])

#    h_pt_vtx_unp.SetLineWidth(2)
#    h_pt_vtx_unp.SetLineColor(R.kBlack)
#    h_pt_vtx_unp.Write()
    
            ######################################
            ###  Extra info from Kalman muons  ###
            ######################################
            #Alberto, is this deprecated in CMSW11?
            #for i in range(nKmtMu):
            #    BX      = int(Kmt_br.bx[i])
            #    qual    = int(Kmt_br.quality[i])
            #    ptVtx   = -1
            #    ptDispl = float(Kmt_br.ptUnconstrained[i])  ## Is there an offset by 1 for displaced muons? - AWB 2019.05.29
            #    eta     = float(Kmt_br.coarseEta[i])*0.010875
            #    chi2    = float(Kmt_br.approxChi2[i])
            #    if VERBOSE: print 'Internal muon %d BX = %d, qual = %d, ptVtx = %.1f, ptDispl = %.1f, eta = %.2f' % (i, BX, qual, ptVtx, ptDispl, eta)
                
            #    if (BX  !=  0): continue
                # if (qual < 12): continue  ## Quality assignment not the same as uGMT quality

            #    h_pt_displ_kmt.Fill( min( max( ptDispl, pt_bins[1]+0.01), pt_bins[2]-0.01) )
            #    h_chi2_kmt    .Fill( min( max( chi2,   chi_bins[1]+0.01), chi_bins[2]-0.01) )

#    c2 = R.TCanvas("c2","Eff",800,600)
#    h_eff_gen_pt.SetStats(0)
#    h_eff_gen_pt.GetXaxis().SetTitle("Gen P_{T} [GeV]")
#    h_eff_gen_pt.GetYaxis().SetTitle("Efficiency")
#    h_eff_gen_pt.GetYaxis().SetRangeUser(0,1.02)

#    h_eff_gen_pt_pt10.SetLineColor(R.kBlue)
#    h_eff_gen_pt_pt20.SetLineColor(R.kRed)

#    h_eff_gen_pt.Draw()
#    h_eff_gen_pt_pt10.Draw("same")
#    h_eff_gen_pt_pt20.Draw("same")

#    leg = R.TLegend(0.5,0.6,0.7,0.8)
#    leg.AddEntry("h_eff_gen_pt", "L1 P_{T} > 0 GeV")
#    leg.AddEntry("h_eff_gen_pt_pt10", "L1 P_{T} > 10 GeV")
#    leg.AddEntry("h_eff_gen_pt_pt20", "L1 P_{T} > 20 GeV")
#    leg.SetLineWidth(0)
#    leg.Draw("same")


#	    with open('EtaPhiDebug.txt', 'a') as f:
#		for i in range(len(dR_list)):
#			Gen_idx = dR_list[i][1]
#			Emu_idx = dR_list[i][2]
#
#			Lxy = sqrt(float(Gen_br.partVx[Gen_idx])**2 + float(Gen_br.partVy[Gen_idx])**2)
#			if Lxy < 30. : continue
#
#			Gen_Eta = float(Gen_br.partEta[Gen_idx])
#			Gen_Eta_prop = getGenEtaBarrel(Gen_br, Gen_idx)
##			Gen_Phi = float(Gen_br.partPhi[Gen_idx])
#			Gen_Phi_prop = getGenPhiBarrel(Gen_br, Gen_idx)	
#			

#			Emu_Eta = float(uGT_br.muonEta[Emu_idx])
#			Emu_Eta_Vtx = float(uGT_br.muonEtaAtVtx[Emu_idx])
#			Emu_Phi = float(uGT_br.muonPhi[Emu_idx])
#			Emu_Phi_Vtx = float(uGT_br.muonPhiAtVtx[Emu_idx])

#			f.write('\n Dxy : %.4f' %(Lxy))
#			f.write('\nGen: EtaVtx, PhiVtx : \t %.4f %.4f' %(Gen_Eta, Gen_Phi))
#			f.write('\nGen: Eta, Phi at MS2 : \t %.4f %.4f' %(Gen_Eta_prop, Gen_Phi_prop))
#			f.write('\n')
#			f.write('\nEmu: EtaVtx, PhiVtx : \t %.4f %.4f' %(Emu_Eta_Vtx, Emu_Phi_Vtx))
#			f.write('\nEmu: Eta, Phi at MS2 : \t %.4f %.4f' %(Emu_Eta, Emu_Phi))
#			f.write('\n--------------------------------------\n')

	    #Plotting dR between Gen Muon and corrected Gen Muon.

#	    for i in GenMus_acc:
#		phi1 = float(Gen_br.partPhi[i])
#		eta1 = float(Gen_br.partEta[i])
#		phi2 = 0 #getGenPhiBarrel(Gen_br, i)
#		eta2 = 0 #getGenEtaBarrel(Gen_br, i)
#		pt = float(Gen_br.partPt[i])

#		dR = deltaR(phi1, phi2, eta1, eta2)
#		dphi = dPhi(phi1, phi2)

#		y = float(Gen_br.partVy[i])
#		x = float(Gen_br.partVx[i])
#
#		alpha = atan(y/x)
#		if y > 0. and x < 0. : alpha = alpha + pi
#		elif y < 0. and x < 0. : alpha = alpha - pi
#		dAlphi = dPhi(alpha, phi2)
	
#		h_gen_dphi_pt.Fill(dphi, pt)
#		h_gen_dalphi_pt.Fill(dAlphi, pt)
#		h_gen_phi_phit.Fill(phi1, phi2)
#		h_gen_alpha_phi.Fill(phi1, alpha)

#		h_gen_dR.Fill(dR)
#		Lxy = sqrt(Gen_br.partVx[i]**2+Gen_br.partVy[i]**2)
		
#		h_gen_dphi_lxy.Fill(dphi, Lxy)
#		h_gen_dalphi_lxy.Fill(dAlphi, Lxy)

#		deta = abs(eta1 - eta2)
#		h_gen_deta_lxy.Fill(deta, Lxy)
#
#		h_gen_dR_Lxy.Fill(Lxy, dR)

#		muHw = R.TLorentzVector()
#		muHw.SetPtEtaPhiM(float(uGT_br.muonIEtUnconstrained[i]-1)*0.5, float(uGT_br.muonIEta[i])*0.010875, (float(uGT_br.muonIPhi[i]))*0.010908, 105.7e-3)
#		pt_phy = mu1.Pt()		
#		pt_Hw = muHw.Pt()
#		ptvtx_phy = float(uGT_br.muonEt[i])
#		ptvtx_Hw = float(uGT_br.muonIEt[i]-1)*0.5
#		eta_phy = mu1.Eta()
#		eta_Hw =  muHw.Eta()
#		phi_phy = mu1.Phi()
#		phi_Hw = muHw.Phi()
		
#		h_uGTMu_pt_pt.Fill(pt_Hw, pt_phy)
#		h_uGTMu_ptvtx_ptvtx.Fill(ptvtx_Hw, ptvtx_phy)
#		h_uGTMu_eta_eta.Fill(eta_Hw, eta_phy)
#		h_uGTMu_phi_phi.Fill(phi_Hw, phi_phy)

#		h_uGTMu_pt_diff.Fill(pt_phy, pt_phy-pt_Hw)
#		h_uGTMu_ptvtx_diff.Fill(ptvtx_phy, ptvtx_phy-ptvtx_Hw)
#		h_uGTMu_phi_diff.Fill(phi_phy, phi_phy-phi_Hw)
#		h_uGTMu_eta_diff.Fill(eta_phy, eta_phy-eta_Hw)


#    h_ptVtx_debug_denom		= R.TH1F('h_ptVtx_debug_denom',		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2])
#    h_ptIVtx_debug_denom	= R.TH1F('h_ptIVtx_debug_denom',	'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2])
#    h_ptDisp_debug_denom	= R.TH1F('h_ptDisp_debug_denom',	'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2])
#    h_ptIDisp_debug_denom	= R.TH1F('h_ptIDisp_debug_denom',	'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2])
#    h_genpt_debug_denom		= R.TH1F('h_genpt_debug_denom',		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2])

#    h_ptVtx_genpt_rel		= R.TH2F('h_ptVtx_genpt_rel', 		'GenPt',		pt_bins[0], pt_bins[1], pt_bins[2], 50, -5., 5.)
#    h_ptIVtx_genpt_rel		= R.TH2F('h_ptIVtx_genpt_rel', 		'GenPt',		pt_bins[0], pt_bins[1], pt_bins[2], 50, -5., 5.)
#    h_ptDisp_genpt_rel		= R.TH2F('h_ptDisp_genpt_rel', 		'GenPt',		pt_bins[0], pt_bins[1], pt_bins[2], 50, -5., 5.)
#    h_ptIDisp_genpt_rel		= R.TH2F('h_ptIDisp_genpt_rel', 	'GenPt',		pt_bins[0], pt_bins[1], pt_bins[2], 50, -5., 5.)

#    h_ptVtx_genpt_dxy		= R.TH2F('h_ptVtx_genpt_dxy', 			'Gen Dxy [GeV]',		dxy_bins[0], dxy_bins[1], dxy_bins[2], 100, -2., 2.)
#    h_ptIVtx_genpt_dxy		= R.TH2F('h_ptIVtx_genpt_dxy',	 		'Gen Dxy [GeV]',		dxy_bins[0], dxy_bins[1], dxy_bins[2], 100, -2., 2.)
#    h_ptDisp_genpt_dxy		= R.TH2F('h_ptDisp_genpt_dxy', 			'Gen Dxy [GeV]',		dxy_bins[0], dxy_bins[1], dxy_bins[2], 100, -2., 2.)
#    h_ptIDisp_genpt_dxy		= R.TH2F('h_ptIDisp_genpt_dxy', 		'Gen Dxy [GeV]',		dxy_bins[0], dxy_bins[1], dxy_bins[2], 100, -2., 2.)

#    h_ptVtx_genpt_qrelpt	= R.TH2F('h_ptVtx_genpt_qrelpt', 		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2], 100, -2., 2.)
#    h_ptIVtx_genpt_qrelpt	= R.TH2F('h_ptIVtx_genpt_qrelpt', 		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2], 100, -2., 2.)
#    h_ptDisp_genpt_qrelpt	= R.TH2F('h_ptDisp_genpt_qrelpt', 		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2], 100, -2., 2.)
#    h_ptIDisp_genpt_qrelpt	= R.TH2F('h_ptIDisp_genpt_qrelpt', 		'Gen Pt',		pt_bins[0], pt_bins[1], pt_bins[2], 100, -2., 2.)


#    h_uGTMu_pt_pt.GetXaxis().SetTitle("Hardware pT [GeV]")
#    h_uGTMu_pt_pt.GetYaxis().SetTitle("Physical pT [GeV]")
#    h_uGTMu_pt_pt.Write()

#    h_uGTMu_phi_phi.GetXaxis().SetTitle("Hardware phi")
#    h_uGTMu_phi_phi.GetYaxis().SetTitle("Physical phi")
#    h_uGTMu_phi_phi.Write()

#    h_uGTMu_eta_eta.GetXaxis().SetTitle("Hardware eta")
#    h_uGTMu_eta_eta.GetYaxis().SetTitle("Physical eta")
#    h_uGTMu_eta_eta.Write()

#    h_uGTMu_ptvtx_ptvtx.GetXaxis().SetTitle("Hardware pT [GeV]")
#    h_uGTMu_ptvtx_ptvtx.GetYaxis().SetTitle("Physical pT [GeV]")
#    h_uGTMu_ptvtx_ptvtx.Write()

######

#    h_uGTMu_pt_diff.GetYaxis().SetTitle("Physical pT [GeV]")
#    h_uGTMu_pt_diff.Write()

#    h_uGTMu_ptvtx_diff.GetYaxis().SetTitle("Physical pT [GeV]")
#    h_uGTMu_ptvtx_diff.Write()

#    h_uGTMu_phi_diff.GetYaxis().SetTitle("Physical phi")
#    h_uGTMu_phi_diff.Write()

#    h_uGTMu_eta_diff.GetYaxis().SetTitle("Physical eta")
#    h_uGTMu_eta_diff.Write()
    
###############################################

#Debug hists

#    h_ptVtx_debug_denom.SetLineWidth(2)
#    h_ptVtx_debug_denom.SetLineColor(R.kBlue)
#    h_ptVtx_debug_denom.Write()

#    h_ptIVtx_debug_denom.SetLineWidth(2)
#    h_ptIVtx_debug_denom.SetLineColor(R.kGreen)
#    h_ptIVtx_debug_denom.Write()

#    h_ptDisp_debug_denom.SetLineWidth(2)
#    h_ptDisp_debug_denom.SetLineColor(R.kRed)
#    h_ptDisp_debug_denom.Write()

#    h_ptIDisp_debug_denom.SetLineWidth(2)
#    h_ptIDisp_debug_denom.SetLineColor(6)
#    h_ptIDisp_debug_denom.Write()

#    h_genpt_debug_denom.SetLineWidth(2)
#    h_genpt_debug_denom.SetLineColor(R.kBlack)
#    h_genpt_debug_denom.Write()

#    h_uGTMu_ptVtx_genpt.Write()
#    h_uGTMu_ptIVtx_genpt.Write()
#    h_uGTMu_ptDisp_genpt.Write()
#    h_uGTMu_ptIDisp_genpt.Write()

#    h_ptVtx_genpt_rel.Write()
#    h_ptIVtx_genpt_rel.Write()
#    h_ptDisp_genpt_rel.Write()
#    h_ptIDisp_genpt_rel.Write()

##################

#    h_ptVtx_genpt_dxy.GetXaxis().SetTitle("Gen Dxy [cm]")
#    h_ptVtx_genpt_dxy.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Constrained, Physical)")
#    h_ptVtx_genpt_dxy.Write()

#    h_ptIVtx_genpt_dxy.GetXaxis().SetTitle("Gen Dxy [cm]")
#    h_ptIVtx_genpt_dxy.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Constrained, Hardware)")
#    h_ptIVtx_genpt_dxy.Write()

#    h_ptDisp_genpt_dxy.GetXaxis().SetTitle("Gen Dxy [cm]")
#    h_ptDisp_genpt_dxy.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Unconstrained, Physical)")
#    h_ptDisp_genpt_dxy.Write()
		
#    h_ptIDisp_genpt_dxy.GetXaxis().SetTitle("Gen Dxy [cm]")
#    h_ptIDisp_genpt_dxy.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Unconstrained, Hardware)")
#    h_ptIDisp_genpt_dxy.Write()

###################

#    h_ptVtx_genpt_qrelpt.GetXaxis().SetTitle("Gen p_{T} [GeV]")
#    h_ptVtx_genpt_qrelpt.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Constrained, Physical)")
#    h_ptVtx_genpt_qrelpt.Write()

#    h_ptIVtx_genpt_qrelpt.GetXaxis().SetTitle("Gen p_{T} [GeV]")
#    h_ptIVtx_genpt_qrelpt.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Constrained, Hardware)")
#    h_ptIVtx_genpt_qrelpt.Write()

#    h_ptDisp_genpt_qrelpt.GetXaxis().SetTitle("Gen p_{T} [GeV]")
#    h_ptDisp_genpt_qrelpt.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Unconstrained, Physical)")
#    h_ptDisp_genpt_qrelpt.Write()

#    h_ptIDisp_genpt_qrelpt.GetXaxis().SetTitle("Gen p_{T} [GeV]")
#    h_ptIDisp_genpt_qrelpt.GetYaxis().SetTitle("#frac{q/p_{T}(L1) - q/p_{T}(Gen)}{q/p_{T}(Gen)} (Constrained, Hardware)")
#    h_ptIDisp_genpt_qrelpt.Write()

##############################################

