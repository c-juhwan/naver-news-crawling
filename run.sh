SEARCH_KEYWORD="삼성전자"
MAX_PAGE="10"
EXACT_SEARCH="True"
START_DATE="20180102"
END_DATE="20210730"
OUTPUT_FILE_PATH="./result/crawling_result_삼성전자.xlsx"

clear
python main.py --search_keyword=${SEARCH_KEYWORD} --max_page=${MAX_PAGE} --exact_search=${EXACT_SEARCH} --start_date=${START_DATE} --end_date=${END_DATE} --output_file_path=${OUTPUT_FILE_PATH}