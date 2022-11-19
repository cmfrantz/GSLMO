// Macro that automates the extraction of color metrics from *.oir confocal images
// Written by Carie Frantz, 2022-08-03

// User selects working directory
dir=getDirectory("Choose source directory ");
filelist=getFileList(dir);
for (i=0; i<filelist.length; i++)
	Wholecolor(dir, filelist[i]);
	
// Define the measurements to run
run("Set Measurements...", "area mean standard modal min median display redirect=None decimal=3");

// Macro for each file	
function Wholecolor (dir,filename){
	// run("Bio-Formats Windowless Importer", "open= + dir + filename color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
	open (dir + filename);
	run("Split Channels");
	close();
	for (j=0; j<3; j++)
		MeasureColor();
}

function MeasureColor(){
	run("8-bit");
	run("Measure");
	close();
}

saveAs("Results", dir+"ColorMeasurements.csv");
run("Clear Results");
