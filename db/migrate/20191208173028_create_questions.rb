class CreateQuestions < ActiveRecord::Migration[6.0]
  def change
  	create_table :questions do |t|
	  	t.string :identifier
	  	t.string :response
	  	t.string :user_hash
	  end
	end
end
