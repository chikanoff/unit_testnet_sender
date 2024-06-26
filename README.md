# Requirements
- Python 3.12.3 (or compatible version)

## Setup and Run Instructions

### 1. create `.env` file with following variables:
> ```dotenv
> SENDER_ADDRESS=sender_address
> PRIVATE_KEY=your_private_key
> ```

### 2. change `script.py`:

> - you can add as many addresses as you want
> ```python 
> recipient_addresses = ["address1", "address2", "address3", ...]
> ```
> 
> - you can change the amount to whatever you want, but I recommend using 0.00001
> ```python
> SEND_AMOUNT = 0.00001 # amount 
> ```
>
> - you can change timings and retries of failure transactions
> ```python
> SENDING_TIMEOUT = 1 # i recommend use 1
> RETRY_TIMEOUT = 3 # time to resend transaction if previous was error
> MAX_RETRIES = 5 # max retries 
> ```

### 3. Install dependencies

> ```sh
> pip install -r requirements.txt
> ```

### 4. Run the script

> ```sh
> python script.py
> ```

### Notes:

- Ensure you have `pip` installed. If not, you can download and install it from the [official site](https://pip.pypa.io/en/stable/installation/).
- If you encounter issues during installation, verify the package versions and ensure your environment has internet access to download the packages.
- Using a virtual environment is recommended to avoid dependency conflicts.

By following these steps, you should be able to set up and run your script successfully.


# Buy Me a Coffee

If you find this project useful and would like to support its development, you can buy me a coffee. I'm just starting to develop in web3. I really need your support!

**TRC-20 Address:** `TEbvib2iYetCV8LjJpKTDvXeEiGpxXAzpo`

Thank you for your support!
