class Question < ActiveRecord::Base
	belongs_to :user

	def self.get_or_create_user_submission user, notebook, identifier
		Question.where(user_id: user.id).where(notebook: notebook).where(identifier: identifier).first_or_initialize
	end

	def self.to_2d_array notebook, questions, user_hashes, usernames
		rows = {}
		if user_hashes || usernames
			rows[0] = ['user'] + questions.sort
		else
			rows[0] = questions
		end

		idx = 1
		relation = Question.where(notebook: notebook, identifier: questions)
		relation.pluck(:user_id).uniq.each do |user|
			row = []
			if user_hashes
				row << User.find(user).hash_username
			elsif usernames
				row << (User.find(user).email || User.find(user).username)
			end
			questions.sort.each do |question|
				begin
					response = relation.where(user_id: user, identifier: question).first.response
				rescue NoMethodError
					response = nil
				end
				row << response
			end
			rows[idx] = row
			idx += 1
		end
		rows
	end

	def self.get_all_notebook_questions notebook, usernames=false
		questions = Question.where(notebook: notebook).pluck(:identifier).uniq
		Question.to_2d_array notebook, questions, false, usernames
	end
end