import json
import ctypes
import sys
import os
import subprocess
import math
import ROOT
from ROOT import TCanvas, TPad, TGraph, TGraphErrors, TGraphAsymmErrors, TFile, TH1F, TLine, TLegend, TMath, TFitResult, TFitResultPtr, TText, TEfficiency

import numpy as np

ROOT.gROOT.SetBatch(True)

class EfficiencyCalculator:


    def __init__(self):
        self.__hipprod = ROOT.TH1F()
        self.__offset = ROOT.TH1F()
        self.__pileup = 0.
        self.__pileup_histo = ROOT.TH1F()
        self.__layer = ''
        self.__deadtime = 0.
        self.__offset_value = 0.
        self.__reweight_factors={}

    def get_pileup(self):
        return self.__pileup
    
    def set_pileup(self,pileup):
        self.__pileup = pileup

    def get_pileup_histo(self):
        return self.__pileup

    def set_pileup_histo(self,pileup_histo):
        #--- if the PU histo is set, it is used instead of the mean value
        self.__pileup_histo = pileup_histo

    def get_fillscheme(self):
        return self.__fillscheme

    def set_fillscheme(self,fillschemepath):
        #--- opening json files - load of the scheme structure 
        #print('setting fill scheme...')
        with open(fillschemepath) as json_input:
            bx_list = json.load(json_input)
        self.__fillscheme = bx_list
        if len(bx_list)==0:
            print('Warning: empty fill scheme')

    def read_inputs(self,hipprobpath,offsetpath):
        #--- opening HIP probability per pile-up 
        #print('setting HIP probabilities...')
        ifileHIPprob = TFile(hipprobpath)
        c_hipprob = ifileHIPprob.Get("Canvas_1")
        ROOT.gROOT.cd()
        h_hipprob = c_hipprob.GetPrimitive("pHIP__1").Clone()
        self.__hipprob = h_hipprob
        ifileHIPprob.Close()

        #--- opening low pile-up offset 
        #print('setting low pile-up offset...')
        ifileOffset = TFile(offsetpath)
        c_Offset = ifileOffset.Get("c1")
        ROOT.gROOT.cd()
        h_Offset = c_Offset.GetPrimitive("pad").GetPrimitive("origin").Clone()
        self.__offset = h_Offset
        ifileOffset.Close()

    def read_deadtime(self,deadtimepath,layer):
        #--- opening dead-time values with errors  
        #print('setting dead time values...')
        nDeadTime=0
        error=0
        with open(deadtimepath,'r') as fndt:
            lndt=fndt.readlines()
            for l in lndt:
                s=l.split()
                if s[0]+' '+s[1] == layer:
                    nDeadTime = float(s[2])
                    error = float(s[3])
        self.__layer = layer
        self.__deadtime = nDeadTime
        self.__error = error
        return nDeadTime,error

    def read_reweight_factors(self,reweightpath):
        #--- correction to describe filling scheme of the fill used to compute the dead-time values
        self.__reweight_factors={}
        with open(reweightpath,'r') as f:
            rs=f.readlines()
            for r in rs:
                c=r.split()
                self.__reweight_factors[c[0]+' '+c[1]] = 1./float(c[2])

    def reweight_scheme(self,layer):
        #--- correction to describe filling scheme of the fill used to compute the dead-time values
        factor=1.
        if layer in self.__reweight_factors:
            factor=self.__reweight_factors[layer]
        #else:
        #    print('Warning: reweighting factor not found for layer', layer, '. Using 1.')
        return factor


    def compute_eff_layer(self,train,layer,useOffsetLowPU=True):
        # hit efficiency computed with dead time model - for a given scheme structure(train),low pile-up offset(TH1), HIP probabilities(TH1),average pile-up,layer
        self.__layer = layer
        Offset_value = 0.
        HIPprob_value = 1.
        h_hipprod = self.__hipprob.Clone()
        pu = self.__pileup
        pu_rew=pu*self.reweight_scheme(layer)
        for x in range(0,(self.__hipprob).GetNbinsX()+1):
            if self.__layer == self.__hipprob.GetXaxis().GetBinLabel(x):
                HIPprob_value = self.__hipprob.GetBinContent(x)*1e-5 #load HIP probability for the given layer
            if self.__layer == self.__offset.GetXaxis().GetBinLabel(x):
                Offset_value = self.__offset.GetBinContent(x) #load low pile-up offset for the given layer
                self.__error_offset_value = self.__offset.GetBinError(x) #save low-pu offset error for the given layer 
        if(useOffsetLowPU==False):
            Offset_value = 1. 
        self.__offset_value = Offset_value
        eff_list = {}
        efficiency = Offset_value
        index = 0
        ineff = HIPprob_value * pu_rew
        #compute the hit efficiency with the 'historical' function
        for bx in range(train[0],train[1]+1):
            if index>0 and float(index) < self.__deadtime:
                efficiency=Offset_value-ineff*index
            if index>0 and float(index) >= self.__deadtime:
                efficiency=Offset_value-ineff*self.__deadtime
            eff_list[bx]=efficiency
            index+=1
        #print(eff_list)

        return eff_list

    def compute_avg_eff_layer(self,layer):
        #print('computing average efficiency over orbit for layer: ',layer)
        idx=0
        value=0.
        for train in self.__fillscheme:
            for bx1 in range(train[0],train[1]+1):
                value+=(self.compute_eff_layer(train,layer,True))[bx1]
                idx+=1
        if idx>0:
            self.__avgefflayer = value/idx
        else:
            self.__avgefflayer = 1.
        return self.__avgefflayer


    def compute_fill_factor(self):
        if len(self.__fillscheme)==0:
            print('Error: empty fill scheme')
            return 0
        if self.__deadtime == 0:
            print('Error: deadtime not set for layer', layer)
            return 0
 
        # Average the impact of the 'historical' function on each bx of the orbit
        # Assumption is made that the recovery is total between 2 trains and that the space between bunches in a train is 25ns
        idx=0
        value=0.
        efficiency = 0.
        fill_factor = 1.

        for train in self.__fillscheme:
            index = 0
            for bx in range(train[0],train[1]+1):
                if float(index) < self.__deadtime:
                    efficiency=index
                if float(index) >= self.__deadtime:
                    efficiency=self.__deadtime
                value+=efficiency
                index+=1
                idx+=1
        if idx>0:
            fill_factor = value/idx
        else:
            print('Warning: no bx found in fill scheme')

        return fill_factor


    def compute_avg_eff_layer_factorized(self,layer,useOffsetLowPU=True):
        # hit efficiency computed with dead time model - for a given scheme structure(train),low pile-up offset(TH1), HIP probabilities(TH1),average pile-up,layer
        #print('computing average efficiency over orbit for layer: ',layer)

        if self.__layer != layer:
            print('Error: deadtime not set for layer', layer)
            return 0.
        if (self.__hipprob).GetNbinsX() == 0:
            print('Error: HIP probabilities not set')
            return 0.
        if (self.__offset).GetNbinsX() == 0:
            print('Error: offset values not set')
            return 0.

        # Get HIP proba and offset value for the given layer
        Offset_value = 0.
        HIPprob_value = 1.
        for x in range(0,(self.__hipprob).GetNbinsX()+1):
            if self.__layer == self.__hipprob.GetXaxis().GetBinLabel(x):
                HIPprob_value = self.__hipprob.GetBinContent(x)*1e-5 #load HIP probability for the given layer
            if self.__layer == self.__offset.GetXaxis().GetBinLabel(x):
                Offset_value = self.__offset.GetBinContent(x) #load low pile-up offset for the given layer
                self.__error_offset_value = self.__offset.GetBinError(x) #save low-pu offset error for the given layer
        if(useOffsetLowPU==False):
            Offset_value = 1.
        self.__offset_value = Offset_value

        # Compute inefficiency factor of the fill scheme
        fill_factor = self.compute_fill_factor()

        # Compute layer efficiency
        # use mean PU if PU distribution is not set
        rew_fact = self.reweight_scheme(layer)
        avg_eff = 0.
        total_weight = 0.
        if self.__pileup_histo.GetNbinsX() < 2:
            pu = self.__pileup
            print(Offset_value, HIPprob_value, pu, rew_fact, fill_factor)
            self.__avgefflayer = Offset_value - HIPprob_value * pu * rew_fact * fill_factor
        else:
            for ibin in range(1, self.__pileup_histo.GetNbinsX()+1):
                if self.__pileup_histo.GetBinContent(ibin) >= 1:
                    pu = self.__pileup_histo.GetBinCenter(ibin)
                    weight = self.__pileup_histo.GetBinContent(ibin)
                    #print(ibin, pu, weight)
                    avg_eff += weight * (Offset_value - HIPprob_value * pu * rew_fact * fill_factor)
                    total_weight += weight
            if total_weight!=0 :
                avg_eff /= total_weight
            else :
                avg_eff = 0.
            self.__avgefflayer = avg_eff

        return self.__avgefflayer

    def compute_error_avg_eff_layer(self,layer): # TO BE CORRECTED
        if self.__offset_value > 0 and self.__deadtime > 0:
            err_avg_eff = ( pow(self.__error_offset_value/self.__offset_value,2) + pow(self.__error/self.__deadtime,2) ) * pow(1-self.__avgefflayer,2)
        else :
            err_avg_eff = 0.
        self.__error_avgeff = err_avg_eff
        return err_avg_eff

    def get_avgeff_layer(self):
        return self.__avgefflayer
