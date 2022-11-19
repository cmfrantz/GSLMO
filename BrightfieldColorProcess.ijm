// Macro that automates the extraction of color metrics from *.tif photomicrographs
// Written by Carie Frantz, 2022-11-18
// Inspired by the batch processing macro Percent_Green by Matthew Ott of the University of Minnesota

// Thresholding settings
minhue = 11;
maxhue = 147;
minsat = 32;
maxsat = 255;
minbrt = 70;
maxbrt = 255;

// User selects working directory
dir=getDirectory("Choose source directory ");
filelist=getFileList(dir);
for (i=0; i<filelist.length; i++)
	ColorThresh(dir, filelist[i]);
	
// Define the measurements to run
run("Set Measurements...", "area area_fraction limit display redirect=None decimal=3");

// Macro for each file	
function ColorThresh(dir,filename){
	// Open the file
	open (dir + filename);
	a=getTitle();
	
	// Set up color thresholding
	// run("Color Threshold...");
	run("HSB Stack");
	run("Convert Stack to Images");
	
	// Set hue
	selectWindow("Hue");
	setThreshold(minhue, maxhue);
	run("Convert to Mask");

	// Set saturation
	selectWindow("Saturation");
	setThreshold(minsat, maxsat);
	run("Convert to Mask");

	// Set brightness
	selectWindow("Brightness");
	setThreshold(minbrt, maxbrt);
	run("Convert to Mask");
	
	// Determine pixels that pass the thresholds
	imageCalculator("AND create", "Hue","Saturation");
	imageCalculator("AND create", "Result of Hue","Brightness");
	
	// Close windows
	selectWindow("Hue");
	close();
	selectWindow("Saturation");
	close();
	selectWindow("Brightness");
	close();
	selectWindow("Result of Hue");
	close();

	// Perform calculations
	selectWindow("Result of Result of Hue");
	rename(a);
	run("8-bit");
	setAutoThreshold("Default");
	//setOption("BlackBackground", false);
	//run("Convert to Mask");
	//run("Analyze Particles...", "  show=Masks display summarize");
	run("Measure");

	// Close final window
	selectWindow(a);
	close();
}

saveAs("Results", dir+"ColorMeasurements.csv");
// run("Clear Results");
