import java.io.*;
public class UpgradeDowngrade
{
	public static void main(String[] args) throws Exception 
	{
	    args[0] = args[0].toLowerCase();
	    if(args[0].equals("upgrade") || args[0].equals("downgrade"))
	    {
	    	String[] cmd = {"sudo","-S", "python", "Upgrade_Downgrade_PassArgument.py", args[0]};
	    	System.out.println(runSudoCommand(cmd));
	    }
	}

	  private static int runSudoCommand(String[] command) throws Exception 
	{
	    Runtime runtime =Runtime.getRuntime();
	    Process process = runtime.exec(command);
	    OutputStream os = process.getOutputStream();
	    os.write("Y@$@r1995\n".getBytes());
	    os.flush();
	    os.close();
	    process.waitFor();
	    System.out.println("Writing Sudo Password");
	    String output = readFile(process.getInputStream());
	    if (output != null && !output.isEmpty()) {
	      System.out.println(output);
	    }
	    String error = readFile(process.getErrorStream());
	    if (error != null && !error.isEmpty()) {
	      System.out.println(error);
	    }
	    return process.exitValue();
	 }

	  private static String readFile(InputStream inputStream) throws Exception 
	{
	    if (inputStream == null) {
	      return "";
	    }
	    StringBuilder sb = new StringBuilder();
	    BufferedReader bufferedReader = null;
	    try {
	      bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
	      String line = bufferedReader.readLine();
	      while (line != null) {
		sb.append(line);
		line = bufferedReader.readLine();
	      }
	      return sb.toString();
	    } finally {
	      if (bufferedReader != null) {
		bufferedReader.close();
	      }
	    }
	  }
}
