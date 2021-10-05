SEARCH_LIST_PATH="./data/id_code.csv"
MAX_PAGE="400"
EXACT_SEARCH="True"
START_DATE="20180102"
END_DATE="20210730"
OUTPUT_FILE_FORMAT="xlsx"
OUTPUT_FILE_PATH="./result/crawling_result_${SEARCH_KEYWORD}.${OUTPUT_FILE_FORMAT}"

clear
python main.py --search_list_path=${SEARCH_LIST_PATH} --max_page=${MAX_PAGE} --exact_search=${EXACT_SEARCH} --start_date=${START_DATE} --end_date=${END_DATE} --output_file_path=${OUTPUT_FILE_PATH}