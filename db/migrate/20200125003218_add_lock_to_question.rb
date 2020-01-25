class AddLockToQuestion < ActiveRecord::Migration[6.0]
  def change
    add_column :questions, :locked, :boolean
  end
end
