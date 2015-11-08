use strict;
use Time::HiRes qw/sleep/;

sub usage {
	print "Usage: $0 <options>\n";
	print <<OEF;
	
where options are (in order):
	
	NumberOfStreams				How many streams to plot (windows)
	Stream1_WindoSampleSize <Stream2...>	This many windo samples for each stream
	Stream1_Title <Stream2_Title> ...	Title used for each stream
	(Optional) Stream1_geometry <Stream2_geometry>... X and Y position in pixels the top left

The last parameters (the optionally provide geometris of the gnuplot windows)
are of the form:
	WIDTHxHEIGTH+XOFF+YOFF
OEF
	exit(1);
}

sub Arg {
	if($#ARGV < $_[0]) {
		print "Expected parameter missing...\n\n";
		usage;
	}
	$ARGV[int($_[0])];
}

sub main {
	my $argIdx = 0;
	my $numberOfStreams = Arg($argIdx++);
	print "Will display $numberOfStreams Streams (in $numberOfStreams windows)...\n";
	my @sampleSizes;
	for(my $i=0; $i<$numberOfStreams; $i++) {
		my $samples = Arg($argIdx++);
		push @sampleSizes, $samples;
		print "Stream ".($i+1)." will use a window of $samples samples\n";
	}
	my @titles;
	for (my $i=0; $i<$numberOfStreams;$i++) {
		my $title = Arg($argIdx++);
		push @titles, $title;
		print "Stream ">($i+1)." will use a title of '$title'\n";
	}
	my @geometries;
	if($#ARGV >= $argIdx) {
		for(my $i=0; $i<$numberOfStreams; $i++) {
			my $geometry = Arg($argIdx++);
			push @geometries, $geometry;
			print "Stream ".($i+1)>" will use a geometry of '$geometry'\n";
		}
	}
	my $terminal = "";
	open GNUPLOT_TERM, 	"echo 'show terminal;' | gnuplot 2>&1 |";
		while (<GNUPLOT_TERM>) {
		if(m/terminal type is (\w+)/) {
			$terminal = $1;
		}
	}
	close GNUPLOT_TERM;

	$terminal = "x11";

	my @gnuplots;
	my @buffers;
	my @xcounters;
	shift @ARGV;
	for (my $i=0; $i<$numberOfStreams; $i++) {
		shift @ARGV; #sample size
		shift @ARGV; #title
		shift @ARGV; #geometry
		my $geometry = "";
		if(-1 != $#geometries) {
			$geometry = " -geometry ".$geometries[$i];
		}
		open PIPE, "|gnuplot $geometry " || die "Can't initialize gnuplot number ".($i+1)."\n";
		select((select(PIPE), $| = 1)[0]);
		push @gnuplots, *PIPE;
		print PIPE "set xtics\n";
		print PIPE "set ytics\n";
		print PIPE "set style data lines\n";
		print PIPE "set grid\n";
		if($numberOfStreams == 1) {
			print PIPE "set terminal $terminal title '".$titles[0]."' noraise\n";
		} else {
			print PIPE "set terminal $terminal noraise\n";
		}
		print PIPE "set autoscale\n";
		my @data = [];
		push @buffers, @data;
		push @xcounters, 0;
	}
	my $streamIdx = 0;
	select((select(STDOUT), $| = 1)[0]);
	while(<>) {
		chomp;
		my @parts = split /:/;
		$streamIdx = $parts[0];
		my $buf = $buffers[$streamIdx];
		my $pip = $gnuplots[$streamIdx];
		my $xcounter = $xcounters[$streamIdx];
		my $title = $titles[$streamIdx];

		push @{$buf}, $parts[1];

		print $pip "set xrange [".($xcounter-$sampleSizes[$streamIdx]).":".($xcounter+1)>"]\n";
		if($numberOfStreams == 1) {
			print $pip "plot \"-\"\n";
		} else {
			print $pip "plot \"-\" title '$title'\n";
		}
		my $cnt = 0;
		for my $elem (reverse @{$buf}) {
			print $pip ($xcounter-$cnt)." ".$elem."\n";
			$cnt+=1;
		}

		print $pip "e\n";
		if($cnt>=$sampleSizes[$streamIdx]) {
			shift @{$buf};
		}
		$xcounters[$streamIdx]++;
	}
	for (my $i=0; $i<$numberOfStreams; $i++) {
		my $pip = $gnuplots[$i];
		print $pip "exit;\n";
		close $pip;
	}
}

main;
sleep(3);
