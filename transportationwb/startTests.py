# testall


def startTests():

	import QtUnitGui
	import transportationwb
	import transportationwb.Test_top
	reload(transportationwb.Test_top)
	#current work tests
	QtUnitGui.addTest("transportationwb.Test_top")
	#generated tests by gentest.py
	QtUnitGui.addTest("transportationwb.Test_top_gen")

	QtUnitGui.addTest("transportationwb.Test_labeltools")
	QtUnitGui.addTest("transportationwb.Test_miki")
	QtUnitGui.addTest("transportationwb.traffic.Test_traffic")
	QtUnitGui.addTest("transportationwb.vehicle.Test_vehicle")
	QtUnitGui.addTest("transportationwb.Test_All.Col1")
