package lime.ui;

/**
 * Stub for lime fork's FileDialogFilter (missing in lime 8.2.2).
 * Used by openfl fork's FileReference for save/download dialogs on mobile.
 */
class FileDialogFilter
{
	public var description:String;
	public var extension:String;

	public function new(description:String = "", extension:String = "")
	{
		this.description = description;
		this.extension = extension;
	}
}
