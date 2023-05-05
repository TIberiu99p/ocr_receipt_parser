import cv2
import pytesseract
import re
import pandas as pd


pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Update this path

def capture_image():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow('Capture Image', frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite('captured_receipt.jpg', frame)
            break

    cap.release()
    cv2.destroyAllWindows()


def parse_receipt(image_path):
    img = preprocess_image(image_path)
    text = pytesseract.image_to_string(img)
    print("OCR Text:\n", text)  # Debugging

    supplier_name = re.search(r'Supplier Name:\s(.+)', text)
    net = re.search(r'Net:\s(.+)', text)
    vat = re.search(r'VAT:\s(.+)', text)
    gross = re.search(r'Gross:\s(.+)', text)
    payment_method = re.search(r'(Cash|Card)', text)

    data = {
        'Supplier Name': supplier_name.group(1) if supplier_name else '',
        'Net': net.group(1) if net else '',
        'VAT': vat.group(1) if vat else '',
        'Gross': gross.group(1) if gross else '',
        'Payment Method': payment_method.group(1) if payment_method else '',
    }

    print("Parsed Data:\n", data)  # Debugging
    return data

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    return thresh



def save_to_excel(data):
    df = pd.DataFrame(data, index=[0])
    df.to_excel('receipt_data.xlsx', index=False)

def main():
    capture_image()
    receipt_data = parse_receipt('captured_receipt.jpg')
    save_to_excel(receipt_data)

if __name__ == '__main__':
    main()
