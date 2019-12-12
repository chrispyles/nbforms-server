class AttendanceSubmission < ActiveRecord::Base
	belongs_to :user
	belongs_to :notebook

	def self.to_2d_array subs, collapse=true
		rows = [['user', 'timestamp', 'was_open']]
		if collapse
			already_added = {}
		end
		if collapse
			subs.pluck(:user_id).uniq.each do |user_id|
				user = User.find(user_id)
				user_subs = subs.where(user_id: user_id, was_open: true).order(submitted: :desc)
				if user_subs.length > 0
					s = user_subs.first
					rows += [[user.email || user.username, s.submitted.to_s, s.was_open]]
				else
					user_subs = subs.where(user_id: user_id, was_open: [false, nil]).order(submitted: :desc)
					if user_subs.length > 0
						s = user_subs.first
						rows += [[user.email || user.username, s.submitted.to_s, s.was_open || false]]
					end
				end
			end
		else
			subs.each do |s|
				user = User.find(s.user_id)
				rows += [[user.email || user.username, s.submitted.to_s, s.was_open]]
			end
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