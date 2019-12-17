class AttendanceSubmission < ActiveRecord::Base
	belongs_to :user
	belongs_to :notebook

	def self.get_most_recent_sub user, notebook
		subs = where(user_id: user.id, notebook_id: notebook.id)
		open_subs = subs.where(was_open: true)
		if open_subs.length > 0
			return open_subs.order(submitted: :desc).first
		end
		closed_subs = subs.where(was_open: [false, nil])
		return closed_subs.order(submitted: :desc).first
	end

	def self.get_all_subs_csv
		nbs = pluck(:notebook_id).uniq.sort()
		headers = ['user']
		nbs.each do |nb|
			headers += ["#{nb}_timestamp", "#{nb}_was_open"]
		end
		rows = [headers]
		pluck(:user_id).uniq.each do |user_id|
			user = User.find(user_id)
			row = [user.email || user.username]
			user_subs = where(user_id: user_id)
			nbs.each do |nb|
				subs = user_subs.where(notebook_id: nb, was_open: true).order(submitted: :desc)
				if subs.length > 0
					row += [subs.first.submitted, true]
					next
				end
				subs = user_subs.where(notebook_id: nb, was_open: [false, nil]).order(submitted: :desc)
				if subs.length > 0
					row += [subs.first.submitted, subs.first.was_open || false]
					next
				end
				row += [nil, nil]
			end
			rows += [row]
		end
		rows
	end


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

	def self.to_csv subs, all=false
		if all
			rows = self.get_all_subs_csv
		else
			rows = self.to_2d_array subs
		end
		csv_string = ""
		rows.each do |row|
			csv_string += row.to_csv
		end
		csv_string
	end
end