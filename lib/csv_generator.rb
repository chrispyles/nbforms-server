require 'csv'

def array_to_csv_string arr
	CSV.generate do |csv|
		arr.each do |subarr|
			csv << subarr
		end
	end
end