class CreateNotebooks < ActiveRecord::Migration[6.0]
  def change
  	create_table :notebooks do |t|
  		t.string :identifier
  		t.boolean :attendance_open
  	end
  end
end
