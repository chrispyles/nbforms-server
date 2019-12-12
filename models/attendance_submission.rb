class AttendanceSubmission < ActiveRecord::Base
	belongs_to :user
	belongs_to :notebook

	def self.to_2d_array subs
		rows = [['user', 'timestamp']]
		subs.each do |s|
			user = User.find(s.user_id)
			rows += [[user.email || user.username, s.submitted.to_s]]
		end
		rows
	end

	def self.to_csv subs
		rows = self.to_2d_array subs
		csv_string = ""
		rows.each do |row|
			csv_string += row.to_csv
		end
		csv_string
	end
end