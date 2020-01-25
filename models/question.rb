class Question < ActiveRecord::Base
	belongs_to :user
	belongs_to :notebook

	def self.filter_for_locks questions, notebook
		i = 0
		to_delete = []
		Question.where(notebook_id: notebook.id, identifier: questions, locked: [false, nil]).map { |q|
			q.identifier
		}
	end

	def self.get_or_create_user_submission user, notebook, identifier
		Question.where(user_id: user.id).where(notebook_id: notebook.id).where(identifier: identifier).first_or_initialize
	end

	def self.to_2d_array notebook, questions, user_hashes, usernames, override_locks=false
		rows = {}
		if !override_locks
			questions = Question.filter_for_locks questions, notebook
		end
		if questions.length == 0
			raise 'No questions'
		end
		if user_hashes || usernames
			rows[0] = ['user'] + questions.sort
		else
			rows[0] = questions.sort
		end

		idx = 1
		relation = Question.where(notebook_id: notebook.id, identifier: questions)
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
		questions = Question.where(notebook_id: notebook.id).pluck(:identifier).uniq
		Question.to_2d_array notebook, questions, false, usernames
	end
end