select table_schema, sum((data_length+index_length)/1024/1024) AS MB from information_schema.tables group by 1;
