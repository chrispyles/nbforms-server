class CreateUsers < ActiveRecord::Migration[6.0]
  def change
  	create_table :users do |t|
  		t.string :username
  		t.string :password_hash
  		t.string :api_key
  		t.string :name
  		t.string :email
  	end
  end
end
