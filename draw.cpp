#include "TH1D.h"

#include "inc/MVAExtra.hh"

using namespace std;

double GetIntegral(TH1 *h){

  double sum=0;
  double dx = (double)(h->GetXaxis()->GetXmax()-h->GetXaxis()->GetXmin())/(double)h->GetNbinsX();
  
  for (int i=0;i<h->GetNbinsX();i++)
    sum+=h->GetBinContent(i+1)*dx;

  return sum;

}

void draw(string channel = "1l",string nj=">=10", string nb=">=4")
{
  
  string file = "output_1l_8ji3bi_0.root";
  string njet = "nJets"+nj;
  string nbjet = "nBTags_MV2c10_70"+nb;
  string name = njet+"_"+nbjet;
  
  name.erase(remove(name.begin(), name.end(), '='), name.end());
  name.erase(remove(name.begin(), name.end(), '>'), name.end());
  name.erase(remove(name.begin(), name.end(), '<'), name.end());

  
  gStyle->SetOptStat(0);
  gStyle->SetHatchesLineWidth(3);
  //TGaxis::SetMaxDigits(2);

  string sig_str = "(class_id&&"+njet+"&&"+nbjet+")*weight";
  string bkg_str = "(!class_id&&"+njet+"&&"+nbjet+")*weight";

  TCut Sig = sig_str.c_str();
  TCut Bckg = bkg_str.c_str();
  
  double ne=80;double xmin=-0.04;double xmax=1.04; string selection = "score";
  
  
  TFile *f = new TFile(file.c_str());
  TTree *test_tr = (TTree*)f->Get("TestTree");
  TTree *train_tr = (TTree*)f->Get("TrainTree");
 
  TH1D *S_t = new TH1D("S_t","Signal",ne,xmin,xmax);
  TH1D *B_t = new TH1D("B_t","Background",ne,xmin,xmax);
  TH1D *S_tr = new TH1D("S_tr","Signal",ne,xmin,xmax);
  TH1D *B_tr = new TH1D("B_tr","Background",ne,xmin,xmax);
  test_tr->Project("S_t",selection.c_str(),Sig);
  test_tr->Project("B_t",selection.c_str(),Bckg);
  train_tr->Project("S_tr",selection.c_str(),Sig);
  train_tr->Project("B_tr",selection.c_str(),Bckg);
  double sfac = ne/(xmax-xmin);
  S_t->Scale(sfac/S_t->Integral());
  B_t->Scale(sfac/B_t->Integral());
  S_tr->Scale(sfac/S_tr->Integral());
  B_tr->Scale(sfac/B_tr->Integral());

  
  TH2F *hcan = new TH2F("hcan","",100,S_t->GetXaxis()->GetXmin(),S_t->GetXaxis()->GetXmax(),100,0.1,26.95);
  hcan->GetXaxis()->SetTitle("NN Output");
  //hcan->GetXaxis()->SetTitle("H_{T} (GeV)");
  hcan->GetYaxis()->SetTitle("1/N (dN/dx)");


  TCanvas *c = new TCanvas("c");
  c->SetTicky(); c->SetTickx();

  S_tr->SetFillStyle(1001); S_tr->SetFillColor(kAzure+7); S_tr->SetLineColor(kAzure+7); S_tr->SetLineWidth(3);
  B_tr->SetFillStyle(3445); B_tr->SetFillColor(kRed-7); B_tr->SetLineColor(kRed-7); B_tr->SetLineWidth(3);
  S_t->SetMarkerStyle(20); S_t->SetMarkerSize(1.7); S_t->SetMarkerColor(4); S_t->SetLineColor(4); S_t->SetLineWidth(3);
  B_t->SetMarkerStyle(20); B_t->SetMarkerSize(1.7); B_t->SetMarkerColor(2); B_t->SetLineColor(2); B_t->SetLineWidth(3);

  hcan->Draw();
  S_tr->Draw("hist same");
  B_tr->Draw("hist same");
  S_t->Draw("e1 same");
  B_t->Draw("e1 same");
  //Sval_t->Draw("hist same");
  //Bval_t->Draw("hist same");

  string namex="10ji3bi";
  TLegend *l_1 = new TLegend(0.0740375,0.823383,0.537019,0.997512);
  l_1->SetLineWidth(3);
  l_1->SetFillStyle(0);
  l_1->SetHeader("      Test Sample");
  l_1->AddEntry(S_t,("Signal @j"+nj+" bj"+nb).c_str(),"p");
  l_1->AddEntry(B_t,("Background @j"+nj+" bj"+nb).c_str(),"p");
  l_1->Draw();
  TLegend *l_2 = new TLegend(0.538993,0.823383,0.994077,0.997512);
  l_2->SetLineWidth(3);
  l_2->SetFillStyle(0);
  l_2->SetHeader("      Train Sample");
  l_2->AddEntry(S_tr,("Signal @j"+nj+" bj"+nb).c_str(),"f");
  l_2->AddEntry(B_tr,("Background @j"+nj+" bj"+nb).c_str(),"f");
  l_2->Draw();

  c->SaveAs(("plots/bdt_"+channel+"_"+name+".png").c_str());


  //-----------------------------------------------------------

  MVAExtra MVAE("MVAE",S_t,B_t);
  MVAExtra MVAE_tr("MVAE_tr",S_tr,B_tr);
  //MVAExtra MVAE_val("MVAE_val",Sval_t,Bval_t);
  
  cout << "Seperation Eval: " << MVAE.GetSeparation()
       << " Seperation Trained: " << MVAE_tr.GetSeparation() << endl;

  //-----------------------------------------------------------

  TCanvas *cg = new TCanvas("cg");
  cg->SetTicky(); cg->SetTickx();

  TH1D *rc_1 = MVAE.GetROC(4);
  TH1D *rc_3 = MVAE_tr.GetROC(4);
  //TH1D *rc_2 = MVAE_val.GetROC(2);

  rc_1->SetLineColor(kGray+3); rc_1->SetLineWidth(5); rc_1->SetLineStyle(1);
  //rc_2->SetLineColor(kRed-4); rc_2->SetLineWidth(5); rc_2->SetLineStyle(9);
  rc_3->SetLineColor(kAzure-3); rc_3->SetLineWidth(5); rc_3->SetLineStyle(1);
  rc_3->SetMarkerColor(kGray+3); rc_3->SetMarkerStyle(20); rc_3->SetMarkerSize(1.6);

  rc_1->Draw("L hist");
  rc_3->Draw("hist L same");
  
  TLatex latex2;
  latex2.SetTextSize(0.035);
  latex2.SetTextAlign(13);  //align at top
  latex2.DrawLatex(0.4,1.01,"ATLAS #bf{internal}");
 
  TLegend *l_4 = new TLegend(0.11846,0.205224,0.82231,0.376866);
  l_4->SetLineWidth(3);
  l_4->SetFillStyle(0);
  l_4->SetHeader(("ROC Curves @j"+nj+" bj"+nb).c_str());
  l_4->AddEntry(rc_1,Form("Test - %1.3f",MVAE.GetSeparation()),"l");
  l_4->AddEntry(rc_3,Form("Train - %1.3f",MVAE_tr.GetSeparation()),"l");
  l_4->Draw();
  
  cg->SaveAs(("../MVA_Data/plots/roc_"+channel+"_"+name+".png").c_str());

}
