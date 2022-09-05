import ctypes
from ROOT import TCanvas, TPad, TGraph, TGraphErrors, TGraphAsymmErrors, TFile, TH1F, TLine, TLegend, TMath, TFitResult, TFitResultPtr, TF1, TAxis, TLatex, TGaxis, TLegend, TLegendEntry
import sys


# Read arguments

if len(sys.argv)<2:
  print('Syntax is: python3 FILE [XMIN XMAX] ')
  exit() 

filename=str(sys.argv[1])
xmin = 0
xmax = 100
if len(sys.argv)>=3:
  xmin=str(sys.argv[2])
if len(sys.argv)>=4:
  xmax=str(sys.argv[3])


layer_names=[]


# Read file data

f = TFile(filename)
d = f.Get('SiStripHitEff')
c = TCanvas()
func = TF1('line', '[0]+[1]*x', 0, 100)

g_offset = TGraphErrors()
g_coeff = TGraphErrors()

h_all = d.Get('all')
nlayer = h_all.GetNbinsX()-1
print('Found', nlayer, 'layers')

offset = []
offset_err = []
coeff = []
coeff_err = []
# Loop over layers
for i in range(1,nlayer+1):
    g_clean = TGraphAsymmErrors()
    g = d.Get('effVsPU_layer'+str(i))
    layername = d.Get('resol_layer_'+str(i)).GetTitle()
    layer_names.append(layername)
    ipt = 0
    if g:
        x = ctypes.c_double(0.0)
        y = ctypes.c_double(0.0)
        for ipu in range(0, g.GetN()+1):
            g.GetPoint(ipu,x,y)
            if y.value>0.01:
                g_clean.SetPoint(ipt,x.value,y.value)
                g_clean.SetPointError(ipt, 0, 0, g.GetErrorYlow(ipu), g.GetErrorYhigh(ipu))
                #print(ipu, ipt, x.value,y.value, g.GetErrorYlow(ipu), g.GetErrorYhigh(ipu))
                ipt+=1
    
        if g_clean.GetN()>2:
            g_clean.SetMarkerStyle(20)
            g_clean.Draw('AP')
    
            r = g_clean.Fit('line', 'SQR')
            print('layer', layername)
            print('fit result: ',r.Chi2(),r.Parameter(0),'+/-',r.ParError(0),r.Parameter(1),'+/-',r.ParError(1))
            c.Print('layer'+str(i)+'.png')
        
            offset.append(r.Parameter(0))
            offset_err.append(r.ParError(0))
            coeff.append(r.Parameter(1)/0.001)
            coeff_err.append(r.ParError(1)/0.001)

        else:
            offset.append(0)
            offset_err.append(0)
            coeff.append(0)
            coeff_err.append(0)

    else:
        offset.append(0)
        offset_err.append(0)
        coeff.append(0)
        coeff_err.append(0)



## Draw like 2018 public results

c1 = TCanvas("c1", "c1",0,53,700,500)
c1.SetHighLightColor(2);
c1.Range(0,0,1,1);
c1.SetFillColor(0);
c1.SetBorderMode(0);
c1.SetBorderSize(2);
c1.SetFrameBorderMode(0);

h1 = TH1F("Offset", "", nlayer, 0, nlayer)
for i in range(1,nlayer+1):
    h1.SetBinContent(i, offset[i-1])
    h1.SetBinError(i, offset_err[i-1])
    h1.GetXaxis().SetBinLabel(i, layer_names[i-1])
h1.SetMinimum(0.99)
h1.SetMaximum(1.00)
h1.SetStats(0)
h1.SetMarkerStyle(8)
h1.SetMarkerColor(2)
h1.SetLineColor(1)
h1.GetXaxis().SetBit(TAxis.kLabelsVert)
h1.GetXaxis().SetLabelFont(42)
h1.GetXaxis().SetLabelOffset(0.003)
h1.GetXaxis().SetLabelSize(0.04)
h1.GetXaxis().SetTitleOffset(1)
h1.GetXaxis().SetTitleFont(42)
h1.GetYaxis().SetTitle("Extrapolated efficiency at PU=0")
h1.GetYaxis().SetLabelColor(2)
h1.GetYaxis().SetLabelFont(42)
h1.GetYaxis().SetTitleSize(0.05)
h1.GetYaxis().SetTitleOffset(0.99)
h1.GetYaxis().SetTitleFont(42)
h1.GetZaxis().SetLabelFont(42)
h1.GetZaxis().SetTitleOffset(1)
h1.GetZaxis().SetTitleFont(42)
h1.Draw("P")

hmin = h1.GetMinimum()
hmax = h1.GetMaximum()

hatched1 = TH1F("hatched1","",nlayer,0,nlayer)
hatched1.SetBinContent(10, hmax)
hatched1.SetBinContent(22, hmax)
hatched1.SetFillColor(1)
#hatched1.SetFillStyle(3004)
hatched1.SetFillStyle(3354)
hatched1.SetLineColor(0);
hatched1.Draw("same hist")

overlay = TPad("overlay", "",0,0,1,1)
overlay.SetFillColor(0)
overlay.SetFillStyle(4000)
overlay.SetBorderMode(0)
overlay.SetBorderSize(2)
overlay.SetFrameFillStyle(4000)
overlay.SetFrameBorderMode(0)
overlay.Draw()
overlay.cd()

h2 = TH1F("Slope", "", nlayer, 0, nlayer)
for i in range(1,nlayer+1):
    h2.SetBinContent(i, coeff[i-1])
    h2.SetBinError(i, coeff_err[i-1])
    h2.GetXaxis().SetBinLabel(i, layer_names[i-1])
h2.SetMinimum(-0.3)
h2.SetMaximum(0)
h2.SetStats(0)
h2.SetMarkerStyle(8)
h2.SetMarkerColor(4)
h2.SetLineColor(1)
h2.GetXaxis().SetBit(TAxis.kLabelsVert)
h2.GetXaxis().SetLabelFont(42)
h2.GetXaxis().SetLabelSize(0)
h2.GetXaxis().SetTitleOffset(1)
h2.GetXaxis().SetTitleFont(42)
h2.GetYaxis().SetLabelFont(42)
h2.GetYaxis().SetLabelSize(0)
h2.GetYaxis().SetTickLength(0)
h2.GetYaxis().SetTitleFont(42)
h2.GetZaxis().SetLabelFont(42)
h2.GetZaxis().SetTitleOffset(1)
h2.GetZaxis().SetTitleFont(42)
h2.Draw("P")

gaxis = TGaxis(nlayer,-0.3,nlayer,0,-0.3,0,510,"+L")
gaxis.SetLabelOffset(0.005)
gaxis.SetLabelSize(0.035)
gaxis.SetTickSize(0.03)
gaxis.SetGridLength(0)
gaxis.SetTitleOffset(0.93)
gaxis.SetTitleSize(0.05)
gaxis.SetTitleColor(1)
gaxis.SetTitleFont(42)
gaxis.SetTitle("#Deltaefficiency /#DeltaPU ( x10^{-3})")
gaxis.SetLabelColor(4)
gaxis.SetLabelFont(42)
gaxis.Draw("same")


hmin = h2.GetMinimum()
hmax = h2.GetMaximum()

line1 = TLine(4,hmin,4,hmax)
line1.SetLineStyle(3)
line1.Draw()
line2 = TLine(10,hmin,10,hmax)
line2.SetLineStyle(3)
line2.Draw()
line3 = TLine(13,hmin,13,hmax)
line3.SetLineStyle(3)
line3.Draw()

leg = TLegend(0.55,0.14,0.86,0.33,"","brNDC");
leg.SetBorderSize(0)
leg.SetTextSize(0.04)
leg.SetLineColor(1)
leg.SetLineStyle(1)
leg.SetLineWidth(1)
leg.SetFillColor(0)
leg.SetFillStyle(0)

entry = leg.AddEntry("origin","#splitline{Extrapolated efficiency}{at PU=0}","P")
entry.SetLineColor(1)
entry.SetLineStyle(1)
entry.SetLineWidth(1)
entry.SetMarkerColor(2)
entry.SetMarkerStyle(8)
entry.SetMarkerSize(1)
entry.SetTextFont(42)

entry = leg.AddEntry("slope","#Deltaefficiency /#DeltaPU","P")
entry.SetLineColor(1)
entry.SetLineStyle(1)
entry.SetLineWidth(1)
entry.SetMarkerColor(4)
entry.SetMarkerStyle(8)
entry.SetMarkerSize(1)
entry.SetTextFont(42)
leg.Draw()
   
#overlay.Modified()
#c1.cd()
tex1 = TLatex(0.9,0.92,"13 TeV")
tex1.SetNDC()
tex1.SetTextAlign(31)
tex1.SetTextFont(42)
tex1.SetTextSize(0.06)
tex1.SetLineWidth(2)
tex1.Draw()
tex2 = TLatex(0.1,0.92,"CMS")
tex2.SetNDC()
tex2.SetTextFont(61)
tex2.SetTextSize(0.075)
tex2.SetLineWidth(2)
tex2.Draw()
tex3 = TLatex(0.22,0.92,"Preliminary")# 2018")
tex3.SetNDC()
tex3.SetTextFont(52)
tex3.SetTextSize(0.057)
tex3.SetLineWidth(2)
tex3.Draw()
c1.Modified()
c1.cd()
c1.Print("EffVsPU_params.png")


# Save results

fout = TFile('PUfit.root', 'recreate')
c1.Write()
h1.Write()
h2.GetXaxis().SetLabelSize(0.04)
h2.GetYaxis().SetLabelSize(0.035)
h2.GetYaxis().SetTickLength(0.03)
h2.GetYaxis().SetTitleOffset(0.93)
h2.GetYaxis().SetTitleSize(0.05)
h2.GetYaxis().SetTitle("#Deltaefficiency /#DeltaPU ( x10^{-3})")
h2.Write()
fout.Close()

