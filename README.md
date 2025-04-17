# RPA - Order Robot - Robocorp Certificate II

A process automation robot to complete the Robocorp course ["Certificate level II: Build a robot"](https://sema4.ai/docs/automation/courses/build-a-robot-python) assignment.

The robot automates the process of ordering several robots via the [RobotSpareBin Industries Inc. website](https://robotsparebinindustries.com/#/robot-order) and can be used as an assistant, which asks for the CSV file URL.


## The automated process

- Open the order page in a web browser
- Request the order file URL from the user using an input dialog
- Download the CSV order file
- Read in the orders information from the CSV file
- For each order in the file:
  - Close modal on order page
  - Fill the form on the website with the order data
  - Preview the soon orderd robot and take ascreenshot of the robot image
  - Submit the order (this step uses the retry logic to avoid xxx  occasional errors on submit)
  - Create a receipt PDF with the robot preview image embedded
  - Trigger ordering of a new robot
- Create a ZIP file of all receipts and store it in the output directory
- Close the browser
- Remove all receipts and screenshot from output directory

