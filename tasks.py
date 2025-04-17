from dataclasses import dataclass
from pathlib import Path

from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables, Table
from RPA.PDF import PDF
from RPA.Archive import Archive

from fpdf import FPDF




"""
Requirements:

Only the robot is allowed to get the orders file. You may not save the file manually on your computer.
The robot should save each order HTML receipt as a PDF file.
The robot should save a screenshot of each of the ordered robots.
The robot should embed the screenshot of the robot to the PDF receipt.
"""


@dataclass
class RobotOrder:
    order_number: str
    head_type: str
    body_type: str
    legs_quantity: str
    ship_address: str


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100, # Each action will be delayed by 100 milliseconds
    )
    open_robot_order_website()
    rows = get_csv_rows()

    for row in rows:
        close_annoying_modal()

        order = RobotOrder(
            order_number=row["Order number"],
            head_type=row["Head"],
            body_type=row["Body"],
            legs_quantity=row["Legs"],
            ship_address=row["Address"]
        )
        fill_and_submit_form(order)
        store_receipt_as_pdf(order.order_number)

        browser.page().click("#order-another")

    archive_receipts()


def open_robot_order_website():
    """
    Opens the Robot Spare Bin website
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_csv_rows() -> Table:
    """
    Downloads the CSV file with all orders that must be made in the Robot Spare Bin site
    """
    http = HTTP()
    http.download(
        "https://robotsparebinindustries.com/orders.csv",
        overwrite=True,
    )
    data = Tables().read_table_from_csv("orders.csv")
    return data


def close_annoying_modal():
    """
    Close the popup that appears when the website is opened
    """
    page = browser.page()
    page.click("//button[text()='OK']")


def fill_and_submit_form(order: RobotOrder):
    page = browser.page()

    page.select_option("#head", order.head_type)
    page.click(f"#id-body-{order.body_type}")
    page.fill("input[placeholder='Enter the part number for the legs']", order.legs_quantity)
    page.fill("input[placeholder='Shipping address']", order.ship_address)
    page.click("#order")

    for _ in range(3):
        alert = page.locator("//div[@class='alert alert-danger']")

        if alert.is_visible():
            page.click("#order")
        else:
            break


def save_receipt_as_pdf(order_number: str):
    page = browser.page()
    receipt = page.locator("#receipt")

    receipt_text = receipt.inner_html()
    screenshot_path = f"output/robots/{order_number}/robot.png"
    receipt.screenshot(path=screenshot_path)

    pdf = PDF()
    pdf.html_to_pdf(receipt_text, f"output/robots/{order_number}/receipt.pdf")
    pdf.add_files_to_pdf(
        files=[screenshot_path],
        target_pdf=f"output/robots/{order_number}/receipt.pdf",
        append=True
    )

def store_receipt_as_pdf(order_number: str):
    save_robot_image(order_number)
    save_receipt_image(order_number)
    generate_pdf(order_number)

def robot_image_path(order_number: str) -> str:
    return f"output/robots/{order_number}/robot.png"

def receipt_image_path(order_number: str) -> str:
    return f"output/robots/{order_number}/receipt.png"

def pdf_path(order_number: str) -> str:
    return f"output/robots/{order_number}/receipt.pdf"

def save_robot_image(order_number: str):
    page = browser.page()
    robot_preview = page.locator("#robot-preview")
    robot_preview.screenshot(path=robot_image_path(order_number))


def save_receipt_image(order_number: str):
    page = browser.page()
    receipt = page.locator("#receipt")
    receipt.screenshot(path=receipt_image_path(order_number))


def generate_pdf(order_number: str):

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add receipt text
    page = browser.page()
    receipt = page.locator("#receipt")
    receipt_text = receipt.inner_text()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, receipt_text)

    # Add robot image
    robot_image = robot_image_path(order_number)
    pdf.add_page()
    pdf.image(robot_image, x=10, y=10, w=100)

    # Add receipt image
    receipt_image = receipt_image_path(order_number)
    pdf.add_page()
    pdf.image(receipt_image, x=10, y=10, w=100)

    # Save the PDF
    pdf.output(pdf_path(order_number))


def archive_receipts():
    """
    Creates a ZIP archive of the receipts and the images.
    """
    archive = Archive()
    path = Path('output/robots')
    archive.archive_folder_with_zip(
        folder=str(path),
        archive_name="output/robot_receipts.zip",
        recursive=True,
    )
