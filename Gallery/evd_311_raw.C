#include <functional>
#include <iostream>
#include <string>
#include <vector>

#include "canvas/Utilities/InputTag.h"
#include "gallery/Event.h"

#include "TFile.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TGraph.h"
#include "TH2I.h"
#include "TH2F.h"
#include "TStyle.h"
#include "TColor.h"
#include "lardataobj/RawData/RawDigit.h"
#include "lardataobj/RecoBase/Wire.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TGaxis.h"
#include "TText.h"

using namespace art;
using namespace std;

// This is a slighlty modified version of Tom Junk's event display "evd_rawdigits.C" tuned for the 3x1x1.
// Many things are hard-coded, to be changed in the future.
// Chirstoph Alt, November 2017
//
// arguments:  filename -- input file, larsoft formatted
// ievcount:  which event to display.  This is the tree index in the file and not the event number
// inputtag:  use "daq" for 3x1x1 data or MC
// autoped:  true if you want to subtract the average of the adc values of a channel before displaying
// minval, maxval -- in order to color the plot well.  Minval: white; Maxval: black

// Example invocation for a 3x1x1 imported rootfile, make an event display for the first event in the file.
// root [0] .L evd_311.C++
// root [1] evd_311("/pnfs/dune/tape_backed/dunepro/test-data/dune/raw/01/85/12/09/wa105_r842_s32_1501156823.root",0);



void
evd_311_gallery_C(std::string const& filename, size_t ievcount, std::string const& rawdigittag="daq", std::string const& recobwiretag="caldata", bool autoped=true, int minval=-10, int maxval=30)
{

  gStyle->SetOptStat(0);
  gStyle->SetPalette(87);

  //gStyle->SetLineWidth(2);

  int nc = 255;
  gStyle->SetNumberContours(nc);
  TH2F* h2tmp = new TH2F("h",";ADC;", nc, minval, maxval, 1, 0, 1);
  for(int i = 1; i <  h2tmp->GetXaxis()->GetNbins()+1; i++){
    double x = h2tmp->GetXaxis()->GetBinCenter(i);
    h2tmp->Fill(x,0.5,x);
  }


  size_t evcounter=0;
  double driftvelocity = 0.16; // cm/us
  double maxdriftdistance = 1667*0.4*driftvelocity; //cm

  InputTag rawdigit_tag(rawdigittag);
  InputTag recobwire_tag(recobwiretag);

  vector<string> filenames(1, filename);

  for (gallery::Event ev(filenames); !ev.atEnd(); ev.next()) {
    if (evcounter == ievcount)
      {

	auto const& recobwire = *ev.getValidHandle<vector<recob::Wire>>(recobwire_tag);
//	auto const& rawdigits = *ev.getValidHandle<vector<recob::Wire>>(recobwire_tag);
	auto const& rawdigits = *ev.getValidHandle<vector<raw::RawDigit>>(rawdigit_tag);
	if (!rawdigits.empty())
	  {
	    size_t nrawdigits = rawdigits.size();
	    size_t nchans=0;
	    for (size_t i=0; i<nrawdigits; ++i)
	      {
		size_t ic = rawdigits[i].Channel();
		if (nchans<ic) nchans=ic;
	      }
	    nchans++;  // set plots to go from channel 0 to the maximum channel we find.

	    size_t nticks = rawdigits[0].Samples();  // assume uncompressed, all channels have the same
                                                    // number of samples.
	    TCanvas *c = new TCanvas("c","c",1198, 422);
				     //1800,500);
	    TPad *pview0 = new TPad("pview0","",0.00,0,0.34,.8);
	    TPad *pview1 = new TPad("pview1","",0.32,0,1,.8);
	    TPad *ptop = new TPad("ptop","",0.0, 0.8, 1., 1.);

	    pview0->Draw();
	    pview0->SetLeftMargin(0.297064);
	    pview0->SetRightMargin(0.1);
	    pview0->SetTopMargin(0.1);
	    pview0->SetBottomMargin(0.17);
	    pview0->SetFillStyle(4000);
	    pview0->SetFrameFillStyle(0);


	    pview1->Draw();
	    pview1->SetLeftMargin(0.02);
	    pview1->SetRightMargin(0.0736522);
	    pview1->SetTopMargin(0.1);
	    pview1->SetBottomMargin(0.17);

	    ptop->Draw();

	    pview0->cd();

	   TH2I *hview0 = (TH2I*) new TH2I("hview0","",320,0,100,nticks,0.,0.4*(1667)); //cm

	    //View 0
	    hview0->SetDirectory(0);
	    for (size_t ichan=0;ichan<320; ++ichan)
	      {
		size_t ic = rawdigits[ichan].Channel();
		int ipedfinal = 0;  // an integer for raw digits
		if (autoped)
		  {
		    const int PedestalIterations = 3;
		    double ped = 0.;
		    double pedthreshold[PedestalIterations] = {10};

		    for(int i=0; i < PedestalIterations; i++)
		    {
		      double csum = 0.;
		      double tickcounter = 0;
		      for (size_t itick=0;itick<nticks;++itick)
		      {
		        if( i == 0 || rawdigits[ichan].ADC(itick) < ped + pedthreshold[i])
			{
			  csum += rawdigits[ichan].ADC(itick);
			  tickcounter+=1;
			}
		      }
		      if(tickcounter < 100) break;
		      csum /= tickcounter;
		      ped = csum;
		    }
		ipedfinal = ped;
		  }
		for (size_t itick=0;itick<nticks;++itick)
		  {
		    hview0->SetBinContent(ic+1,itick+1,rawdigits[ichan].ADC(nticks-itick-1)-ipedfinal);
		    //		    hview0b->SetBinContent(ic+1,itick+1,rawdigits[ichan].ADC(nticks-itick-1)-ipedfinal);
		  }
	      }


	   TH2I *hview1 = (TH2I*) new TH2I("hview1","",960,0,300,nticks,0.,0.4*(1667)); //cm


	    //View 1
	    hview1->SetDirectory(0);
	    for (size_t ichan=320;ichan<nrawdigits; ++ichan)
	      {
		size_t ic = rawdigits[ichan].Channel();
		int ipedfinal = 0;  // an integer for raw digits
		if (autoped)
		  {
		    const int PedestalIterations = 2;

		    double ped = 0.;
		    double pedthreshold[PedestalIterations] = {10};

		    for(int i=0; i < PedestalIterations; i++)
		    {
		      double csum = 0.;
		      double tickcounter = 0;
		      for (size_t itick=0;itick<nticks;++itick)
		      {
		        if( i == 0 || rawdigits[ichan].ADC(itick) < ped + pedthreshold[i])
			{
			  csum += rawdigits[ichan].ADC(itick);
			  tickcounter+=1;
			}
		      }
		      if(tickcounter < 100) break;
		      csum /= tickcounter;
		      ped = csum;
		    }
		ipedfinal = ped;
		  }

		for (size_t itick=0;itick<nticks;++itick)
		  {

		    hview1->SetBinContent(ic+1-320,itick+1,rawdigits[ichan].ADC(nticks-itick-1)-ipedfinal);
		  }
	      }

	    double LabelSizeValue = 0.06;
	    double TitleSizeValue = 0.06;

	    gStyle->SetTitleSize(TitleSizeValue,"t");


            hview0->SetMinimum(minval);
	    hview0->SetMaximum(maxval);

	    hview0->GetXaxis()->SetLabelSize(LabelSizeValue);
	    hview0->GetXaxis()->SetLabelOffset(0.01);
	    hview0->GetXaxis()->SetTitleOffset(1.2);
   	    hview0->GetXaxis()->SetTitleSize(TitleSizeValue);
	    hview0->GetXaxis()->SetNdivisions(4);
	    hview0->GetXaxis()->SetTitle("View 0 [cm]");
	    hview0->GetXaxis()->CenterTitle(kTRUE);

	    hview0->GetYaxis()->SetLabelSize(LabelSizeValue);
	    hview0->GetYaxis()->SetLabelOffset(999);
	    hview0->GetYaxis()->SetTitleSize(TitleSizeValue);
	    hview0->GetYaxis()->SetTitleOffset(1.4);
	    hview0->GetYaxis()->SetTitle("Drift time [#mus]");
	    hview0->GetYaxis()->SetNdivisions(7);
            hview0->GetYaxis()->SetTickLength(0);

	    hview0->Draw("col");




       	    gPad->Update();
            TGaxis *axisv0l = new TGaxis(gPad->GetUxmin(),
                                    gPad->GetUymax(),
                                    gPad->GetUxmin()-0.001,
                                    gPad->GetUymin(),
                                    hview0->GetYaxis()->GetXmin(),
                                    hview0->GetYaxis()->GetXmax(),
                                    510,"R");
            axisv0l->SetLabelFont(132);
            axisv0l->SetLabelSize(LabelSizeValue);
            axisv0l->SetLabelOffset(-0.01);
            axisv0l->SetNdivisions(7);
            axisv0l->Draw();
            TGaxis *axisv0r = new TGaxis(gPad->GetUxmax(),
                                    gPad->GetUymax(),
                                    gPad->GetUxmax()-0.001,
                                    gPad->GetUymin(),
                                    hview0->GetYaxis()->GetXmin(),
                                    hview0->GetYaxis()->GetXmax(),
                                    510,"-L");
            axisv0r->SetLabelFont(132);
            axisv0r->SetLabelSize(LabelSizeValue);
            axisv0r->SetLabelOffset(30000);
            axisv0r->SetNdivisions(7);
            axisv0r->Draw();

	    pview1->cd();

            hview1->SetMinimum(minval);
	    hview1->SetMaximum(maxval);

	    hview1->GetXaxis()->SetLabelSize(LabelSizeValue);
	    hview1->GetXaxis()->SetTitleSize(TitleSizeValue);
//	    hview1->GetXaxis()->SetTitle("Channel");
	    hview1->GetXaxis()->SetLabelOffset(0.01);
	    hview1->GetXaxis()->SetTitleOffset(1.2);
	    hview1->GetXaxis()->SetTitle("View 1 [cm]");
	    hview1->GetXaxis()->SetNdivisions(10);
	    hview1->GetXaxis()->SetTickLength(0.025);
	    hview1->GetXaxis()->CenterTitle(kTRUE);

	    hview1->GetYaxis()->SetLabelSize(LabelSizeValue);
	    hview1->GetYaxis()->SetLabelOffset(30000);
	    hview1->GetYaxis()->SetTickLength(0);
	    hview1->GetYaxis()->SetTitleSize(TitleSizeValue);
	    hview1->GetYaxis()->SetTitleOffset(1.2);
	    hview1->GetYaxis()->SetTitle("Drift time [#mus]");
	    hview1->GetYaxis()->SetNdivisions(7);
	    hview1->GetYaxis()->SetTickLength(0.01);
	    /*
	    hview1->GetZaxis()->SetLabelSize(LabelSizeValue);
	    hview1->GetZaxis()->SetTitle("ADC");
	    hview1->GetZaxis()->SetTitleOffset(0.5);
	    hview1->GetZaxis()->SetTitleSize(TitleSizeValue);
	    */

	    hview1->Draw("col");

	    //       	    hview1->GetYaxis()->SetLabelOffset(999);


       	    gPad->Update();
            TGaxis *axisv1l = new TGaxis(gPad->GetUxmin(),
					 gPad->GetUymax(),
					 gPad->GetUxmin()-0.001,
					 gPad->GetUymin(),
					 hview1->GetYaxis()->GetXmin(),
					 hview1->GetYaxis()->GetXmax(),
					 510,"R");
            axisv1l->SetLabelFont(132);
            axisv1l->SetNdivisions(7);
            axisv1l->SetLabelSize(0);
            axisv1l->SetLabelOffset(300000);
	    axisv1l->SetTickLength(0.1);
            axisv1l->Draw();

	    TGaxis *axisv1r = new TGaxis(gPad->GetUxmax(),
					 gPad->GetUymax(),
					 gPad->GetUxmax()-0.001,
					 gPad->GetUymin(),
					 hview1->GetYaxis()->GetXmin(),
					 hview1->GetYaxis()->GetXmax(),
					 510,"-L");
            axisv1r->SetLabelFont(132);
            axisv1r->SetNdivisions(7);
            axisv1r->SetLabelSize(0);
            axisv1r->SetLabelOffset(300000);
	    axisv1r->SetTickLength(0.1);
            axisv1r->Draw();





	    ptop->cd();
	    gPad->SetTickx(0);
	    ptop->SetLeftMargin(0.101002);
	    ptop->SetRightMargin(0.0500835);
	    ptop->SetTopMargin(0.747368);
	    ptop->SetBottomMargin(0.0105263);

	    h2tmp->GetYaxis()->SetLabelSize(0.);
	    h2tmp->GetYaxis()->SetNdivisions(0);

	    h2tmp->GetXaxis()->SetLabelSize(0.2);
	    h2tmp->GetXaxis()->SetLabelOffset(0.008);
	    h2tmp->GetXaxis()->SetTickLength(0.16);
	    h2tmp->GetXaxis()->SetNdivisions(210);
	    h2tmp->GetXaxis()->SetTitleSize(0.3);
	    h2tmp->GetXaxis()->SetTitleOffset(0.75);

	    h2tmp->Draw("colX+");

	    c->SaveAs("newtest.png");
	  }
      }
    ++evcounter;
  }
}

/*
       // Remove the current axis
       h->GetYaxis()->SetLabelOffset(999);
       h->GetYaxis()->SetTickLength(0);


       // Redraw the new axis
       gPad->Update();
       TGaxis *newaxis = new TGaxis(gPad->GetUxmin(),
                                    gPad->GetUymax(),
                                    gPad->GetUxmin()-0.001,
                                    gPad->GetUymin(),
                                    h->GetYaxis()->GetXmin(),
                                    h->GetYaxis()->GetXmax(),
                                    510,"R");
       newaxis->SetLabelFont(42);
       newaxis->SetLabelSize(fLabelSizeValue);
       newaxis->SetLabelOffset(-0.01);
//       newaxis->SetTitle("Ticks");
//       newaxis->SetTitleFont(42);
//       newaxis->SetTitleSize(0.075);
//       newaxis->SetTitleOffset(-0.03);
       newaxis->Draw();

       // Redraw second new axis
       gPad->Update();
       TGaxis *newaxis2 = new TGaxis(gPad->GetUxmin(),
                                    gPad->GetUymax(),
                                    gPad->GetUxmin()-0.001,
                                    gPad->GetUymin(),
                                    fmaxdriftdistance,
				    0,
                                    510,"R");
       newaxis2->SetLabelFont(42);
       newaxis2->SetLabelSize(fLabelSizeValue);
       newaxis2->SetLabelOffset(-0.01);
       newaxis->SetTitle("Drift Distance");
       newaxis->SetTitleFont(42);
//       newaxis->SetTitleSize(0.075);
//       newaxis->SetTitleOffset(-0.03);
       newaxis2->Draw();
*/
