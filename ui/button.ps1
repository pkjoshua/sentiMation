# Load the Windows Forms assembly
[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")

# Create a form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Sample Windows UI"
$form.Size = New-Object System.Drawing.Size(300, 150)

# Create a button
$button = New-Object System.Windows.Forms.Button
$button.Text = "Click Me!"
$button.Location = New-Object System.Drawing.Point(100, 50)

# Define an event handler for the button click event
$button.Add_Click({
    # This code will run when the button is clicked
    [System.Windows.Forms.MessageBox]::Show("Button Clicked!")
})

# Add the button to the form
$form.Controls.Add($button)

# Show the form
$form.ShowDialog()

# Dispose of the form when done
$form.Dispose()
