import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class createMatrixTxt {
    public static String bugNumberString = "1", additional_files_path = "", outputFileNameEyal = "", outputFileNameAmir = "", inputFile = "", regularMatrixTextFolder = "C:\\Users\\eyalhad\\Desktop\\Math_data\\AmirTxtData";
    public static String[] bugFuncNames;
    public static ArrayList<Integer> bugNumbers =new ArrayList<Integer>();
    public static int category, epsilon = 30, delta = 30;
    public static Map<String, List<String>> traceDic = new HashMap<String, List<String>>();
    public static Map<String, Integer> testFuncDic = new  HashMap<String,Integer>(), funcNumberDic = new HashMap<String, Integer>();

    public static void main(String[] args) throws IOException {
        System.out.println("\n--------Start Create Matrix Txt----------");
        if(args.length>2)
        {
            init_addresses(args);
        }

        category = 1;
        getTestsAndBugNum(inputFile);
        System.out.println("--------CREATE AMIR FILE----------");
        StringBuilder failTestClass = writeTextFile(traceDic,outputFileNameAmir,funcNumberDic);
        if(failTestClass.length()== 0)
            sendFeedback(additional_files_path+ "\\errorFile.txt", 1);
        else {
        category = 3;
        System.out.println("--------CREATE EYAL FILE----------");
        writeTextFile(traceDic,outputFileNameEyal,funcNumberDic);
        category = 2;
        enterFailTestToFiles(failTestClass, outputFileNameAmir);
        enterFailTestToFiles(failTestClass, outputFileNameEyal);
        sendFeedback(additional_files_path + "\\errorFile.txt", 0);
//        File destFile=new File(regularMatrixTextFolder + "\\" + getProjectVersion(additional_files_path) + "_" + bugNumberString + ".txt");
//        if(!destFile.exists())
//        {
//            File sourceFile=new File(outputFileNameAmir);
//            copyFileUsingJava7Files(sourceFile,destFile);
//        }

        }


    }

    private static String getProjectVersion(String additional_files_path) {
        return additional_files_path.split("Desktop")[1].split("_")[0].substring(1);

    }

    private static void copyFileUsingJava7Files(File source, File dest) throws IOException {
        Files.copy(source.toPath(), dest.toPath());
    }

    private static void sendFeedback(String errorFilePath, int i) throws FileNotFoundException, UnsupportedEncodingException {
        PrintWriter writer = new PrintWriter(errorFilePath, "UTF-8");
        writer.println(Integer.toString(i));
        writer.close();
    }


    private static void getTestsAndBugNum(String path) throws IOException {

        int funcIndex=0;
        String line;
        int indexToInsert=0;
        String[] lineData = new String[4];

        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            br.readLine(); //remove first line
            //read the csv input file
            while ((line = br.readLine()) != null) {

                lineData[indexToInsert] = line;
                indexToInsert++;
                if(indexToInsert % 4 == 0)
                {
                    indexToInsert = 0;
                    String testFuncNamesConcate = lineData[0] + lineData[1];
                    //create funcNumberDic to get number for every function
                    if(!funcNumberDic.containsKey(lineData[1]))
                    {
                        funcNumberDic.put(lineData[1],funcIndex);
                        funcIndex++;
                    }

                    //dic for check that we didn't double insert the same combination
                    if(!testFuncDic.containsKey(testFuncNamesConcate))
                    {
                        testFuncDic.put(testFuncNamesConcate,1);
                        //if the function actually in the trace or if we think it is we should add it to the traceDic
                        if(!lineData[2].equals("0.0") || lineData[3].equals("1"))
                        {
                            if (!traceDic.containsKey(lineData[0])) {
                                traceDic.put(lineData[0], new ArrayList<String>());
                            }
                            traceDic.get(lineData[0]).add(lineData[1] + "=" + lineData[2] + "=" + lineData[3]);
                        }
                    }
                }
            }
        }
        updateBugsNumbers(funcNumberDic);
    }

    private static void updateBugsNumbers(Map<String,Integer> funcDic) {
        for(int i=0;i<bugFuncNames.length;i++)
        {
            if(funcDic.containsKey(bugFuncNames[i]))
            {
                if(!bugNumbers.contains(funcDic.get(bugFuncNames[i])))
                    bugNumbers.add(funcDic.get(bugFuncNames[i]));
            }
        }

    }

    private static StringBuilder writeTextFile(Map<String, List<String>> testsFunctionDetails, String textOutputFileName, Map<String, Integer> funcDic) throws FileNotFoundException, UnsupportedEncodingException {

//        File file = new File(textOutputFileName);
//        file.delete();
        PrintWriter writer = new PrintWriter(textOutputFileName, "UTF-8");
        StringBuilder failedTestForInit = new StringBuilder(""), CompNames = new StringBuilder("["), priors = new StringBuilder("["), bugListToFile = new StringBuilder("["), initTestListToFile = new StringBuilder("[");
        StringBuilder trace = new StringBuilder(), predictionTrace = new StringBuilder(), traceWithNoise = new StringBuilder(), act_trace = new StringBuilder();
        boolean bug,havePrediction,haveAct,hadFailedTest = false;
        String noise;

        writeWithoutTrace(testsFunctionDetails, funcDic, writer, CompNames, priors, bugListToFile, initTestListToFile);

        //////////////////////////////traces///////////////////////////////

        for (Map.Entry<String, List<String>>  testEntry : testsFunctionDetails.entrySet()) {
            trace.setLength(0);
            predictionTrace.setLength(0);
            traceWithNoise.setLength(0);
            act_trace.setLength(0);
            String key = testEntry.getKey();
            List<String> functionAndPrediction = testEntry.getValue();
            trace.append(key).append(";");
            predictionTrace.append("{");
            traceWithNoise.append("{");
            act_trace.append("[");
            bug = false;
            havePrediction = false;
            haveAct = false;
            for(int k=0;k<functionAndPrediction.size();k++)
            {
                String [] values = functionAndPrediction.get(k).split("=");
                int compNum= funcDic.get(values[0]);
                havePrediction = haveProbabilityToBeInTrace(havePrediction, predictionTrace, values[1], compNum);
                // if it actually in the trace
                if(Integer.valueOf(values[2])==1)
                {
                    Random generator = new Random();
                    int number = generator.nextInt(epsilon);
                    double result = number / 100.0;
                    noise = String.valueOf(1-result);
                    traceWithNoise.append(compNum).append(":").append(noise).append(", "); // add to the list with the noise
                    act_trace.append(compNum).append(", "); // the actual trace
                    haveAct = true;
                    if(bugNumbers.contains(compNum ))
                        bug = true;
                }
                else{
                    Random generator = new Random();
                    int number = generator.nextInt(delta);
                    double result = number / 100.0;
                    noise = String.valueOf(0 + result);
                    traceWithNoise.append(compNum).append(":").append(noise).append(", ");
                }

            }

            setListsLengthAndClose(havePrediction, haveAct, predictionTrace, traceWithNoise, act_trace);

            editTheTraceToInsertByCategory(trace, predictionTrace, traceWithNoise, act_trace);

            if(bug)
            {
                trace.append("1");
                if(hadFailedTest==false)
                {
                    failedTestForInit.append(key);
                    hadFailedTest = true;
                }
            }
            else
                trace.append("0");
            if(haveAct)
                writer.println(trace);
        }
        writer.close();
        return failedTestForInit;
    }

    private static void editTheTraceToInsertByCategory(StringBuilder trace, StringBuilder predictionTrace, StringBuilder traceWithNoise, StringBuilder act_trace) {
        if(category==1)
            trace.append(act_trace);
        else if (category==2)
            trace.append(act_trace).append(traceWithNoise);
        else
            trace.append(act_trace).append(predictionTrace);
    }

    private static void setListsLengthAndClose(boolean havePrediction, boolean haveAct, StringBuilder predictionTrace, StringBuilder traceWithNoise, StringBuilder act_trace) {
        if(havePrediction)
            predictionTrace.setLength(predictionTrace.length() - 2);

        if(haveAct)
        {
            act_trace.setLength(act_trace.length() - 2);
            traceWithNoise.setLength(traceWithNoise.length() - 2);
        }
        predictionTrace.append("};");
        act_trace.append("];");
        traceWithNoise.append("};");
    }

    private static boolean haveProbabilityToBeInTrace(boolean havePrediction, StringBuilder predictionTrace, String value, int compNum) {
        if(Float.parseFloat(value)>0)
        {
            predictionTrace.append(compNum).append(":").append(value).append(", "); //add the prob
            havePrediction = true;
        }
        return havePrediction;
    }

    private static void writeWithoutTrace(Map<String, List<String>> dataMap, Map<String, Integer> funcDic, PrintWriter writer, StringBuilder compNames, StringBuilder priors, StringBuilder bugListToFile, StringBuilder initTestListToFile) {
        writer.println("[Description]");
        writer.println("default description");
        writer.println("[Components names]");
        //writing comp names with numbers, and priors
        createCompNamesAndPriors(funcDic, compNames, priors);
        writer.println(compNames);
        writer.println("[Priors]");
        writer.println(priors);
        writer.println("[Bugs]");
        createBugListToFile(bugListToFile);
        writer.println(bugListToFile);
        writer.println("[InitialTests]");
        createInitTestsToFile(dataMap, initTestListToFile);
        writer.println(initTestListToFile);
        writer.println("[TestDetails]");
    }

    private static void createInitTestsToFile(Map<String, List<String>> dataMap, StringBuilder initTestListToFile) {
        //writing the initial tests
        int initTestCount=0;
        for (Map.Entry<String, List<String>>  entry : dataMap.entrySet()) {

            initTestListToFile.append("'").append(entry.getKey()).append("'");
            if(initTestCount!=4)
            {
                initTestListToFile.append(", ");
                initTestCount++;
            }
            else
                break;
        }
        initTestListToFile.append("]");
    }

    private static void createBugListToFile(StringBuilder bugListToFile) {
        if(bugNumbers.size()==1)
        {
            bugListToFile.append(String.valueOf(bugNumbers.get(0)));
            bugListToFile.append("]");
        }else {

            for(int k = 0; k< bugNumbers.size(); k++)
            {
                bugListToFile.append(String.valueOf(bugNumbers.get(k)));
                if(k!= bugNumbers.size()-1)
                    bugListToFile.append(",");
            }
            bugListToFile.append("]");
        }
    }

    private static void createCompNamesAndPriors(Map<String, Integer> funcDic, StringBuilder compNames, StringBuilder priors) {
        int i=1;
        for (Map.Entry<String, Integer> entry : funcDic.entrySet()) {
            String key = entry.getKey();
            int value = entry.getValue();
            compNames.append("(").append(value).append(", '").append(key).append("')");
            priors.append("0.1");
            if(i!=funcDic.size())
            {
                compNames.append(", ");
                priors.append(", ");
            }
            i++;
        }
        priors.append("]");
        compNames.append("]");
    }

    private static void enterFailTestToFiles(StringBuilder failTest, String outputFile) throws IOException {

        List<String> fileContent = new ArrayList<>(Files.readAllLines(Paths.get(outputFile), StandardCharsets.UTF_8));
        for (int i = 0; i < fileContent.size(); i++) {
            if(fileContent.get(i).contains("[InitialTests]"))
            {
                i++;
                String line= lineWithoutInitTestsWithoutTrace(fileContent.get(i),outputFile);
                //if there is no fail tests to add
                if(failTest.length()>1)
                {
                    line = line.substring(0,line.length()-1);
                    String newLine = line + ", '" + failTest +"']";
                    fileContent.set(i, newLine);
                }
                else {
                    //remove from line the tests withput trace
                    fileContent.set(i, line);
                }
            }
        }
        Files.write(Paths.get(outputFile), fileContent, StandardCharsets.UTF_8);
    }

    private static String lineWithoutInitTestsWithoutTrace(String line, String outputFile) throws IOException {
        String[] names = line.split(",");
        for(int i=0;i<names.length;i++) {
            names[i]= names[i].substring(names[i].indexOf("'")+1);
            names[i] = names[i].substring(0,names[i].indexOf("'"));
        }
        StringBuilder initTest = new StringBuilder("[");
        String[] newNames = removeNotExistingTests(names,outputFile);
//        check if something got deleted
        if(names.length == newNames.length)
            return line;
        for(int k=0; k<newNames.length;k++)
        {
            initTest.append("'").append(newNames[k]);
            if(k!=newNames.length-1)
                initTest.append("', ");
            else
                initTest.append("'");
        }
        initTest.append("]");
        String toReturn = initTest.toString();
        return toReturn;
    }

    private static String[] removeNotExistingTests(String[] testNames, String outputFile) throws IOException {

        List<String> fileContent = new ArrayList<>(Files.readAllLines(Paths.get(outputFile), StandardCharsets.UTF_8));
        List<String> list = new ArrayList<String>();
        int i;
        for (i = 0; i < fileContent.size(); i++) {
            if (fileContent.get(i).contains("[TestDetails]")) {
                    break;

            }
        }
        i++;
        for (; i < fileContent.size(); i++) {
            String line=fileContent.get(i);
            line = line.split(";")[0];
            for(int k=0;k<testNames.length;k++) {

                if(line.equals(testNames[k])) {
                   if(!list.contains(testNames[k]))
                       list.add(testNames[k]);
                }
            }
            if(list.size()==testNames.length)
                break;
        }

        String[] str_array = list.toArray(new String[0]);

        return str_array;
    }

    private static void init_addresses(String[] args) {
        bugNumberString = args[0];
        String input_bug_fanctions = args[1];
        bugFuncNames = input_bug_fanctions.split(" ");
        additional_files_path = args[2];
        outputFileNameEyal = additional_files_path + "\\inputMatrix_eyal.txt";
        outputFileNameAmir = additional_files_path + "\\inputMatrix_amir.txt";
        inputFile = additional_files_path + "\\input_diagnoser.csv";
    }

}