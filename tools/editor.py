from appJar import gui

app = gui("IFASP Editor", useTtk=True)

app.setTtkTheme("clam")
app.setResizable(False)
app.startNotebook("Notebook")
app.decreaseFont()




app.startNote("Armor") # ARMOR TAB

app.setPadding([10, 5])
app.addListBox("lb_armor_list", [], row = 1, column = 1, rowspan = 4)

app.addVerticalSeparator(row = 1, column = 2, rowspan = 8)

app.addLabel("l_armor_name", "Name", row = 1, column = 3)
app.addEntry("tb_armor_name", row = 1, column = 4, colspan = 2)

app.addLabel("la_armor_desc", "Description", row = 2, column = 3)
app.addTextArea("tx_armor_desc", row = 2, column = 4, rowspan = 1, colspan = 1)

app.addLabel("la_armor_type", row = 3, column = 3)
app.addOptionBox("ob_armor_type", ["Head", "Neck", "Chest", "Legs", "Feet", "Hands"], row = 3, column = 4)

app.addLabel("la_armor_rari", "Rarity", row = 4, column = 3)
app.addOptionBox("ob_armor_rari", ["Common", "Rare", "Mythic", "Antique", "Divine"], row = 4, column = 4)

app.addLabel("la_armor_size", "Size", row = 1, column = 7)
app.addNumericEntry("tb_armor_size", row = 1, column = 8, colspan = 1)



app.stopNote()

"""app.startNote("Weapons")
# WEAPONS TAB
app.setPadding([5, 5])



app.stopNote()
app.stopNote()

app.startNote("Maps")
# MAPS TAB
app.setPadding([5, 5])



app.stopNote()"""




app.stopNotebook()
app.go()